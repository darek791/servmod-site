"""Google Play Billing: POST /api/shop/play/redeem (KONTRAKT 1.8). DESIGN, NOT DEPLOYED, nothing is sent to Google until the owner
installs a service-account key. Without the key every call answers 503 (dry run).

How it works
- The app (play flavour) sends device_id, product (pro|sub), purchase_token, package.
- The server asks Google (never trusts the app): product, package, state. Only then it acknowledges the purchase and ONLY THEN
  issues the activation code (acknowledge first: otherwise Google refunds after 3 days and the user keeps the code).
- One purchase (for a subscription: the whole linkedPurchaseToken chain) = one entitlement with 3 seats (PLAY_DEVICE_LIMIT).
  Every phone of the buyer gets its own WL1 code for its own Device ID. More than 3 devices only through support.
- Codes are issued by issuing.issue(), so the Box firmware check (X-Licence) and revoking work exactly as for shop licences.
- Refunds: worker asks the Voided Purchases API once a day; a voided purchase revokes its entitlement and blocks new redeems.

Environment (/etc/servmod/pay.env, typed on the PC, never in the repo):
  PLAY_KEY_FILE      path to the Google service-account JSON key (read on the server only)
  PLAY_PACKAGE       default com.servmod.app
  PLAY_DEVICE_LIMIT  default 3
  PLAY_SUB_GRACE_DAYS default 3 (days added after the end of the paid period, for phones without internet)
"""
import base64, datetime, json, logging, os, re, threading, time
import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from fastapi import APIRouter, HTTPException, Request
from . import core, issuing

log = logging.getLogger("servmod.play")
router = APIRouter()

SKU = {"pro": "servmod_pro", "sub": "servmod_sub"}
API = "https://androidpublisher.googleapis.com/androidpublisher/v3/applications"
OK_SUB_STATES = {"SUBSCRIPTION_STATE_ACTIVE", "SUBSCRIPTION_STATE_CANCELED"}  # canceled = paid until the end of the period
PENDING_SUB = "SUBSCRIPTION_STATE_PENDING"


def package(): return os.environ.get("PLAY_PACKAGE", "com.servmod.app")
def device_limit():
    try: return max(1, int(os.environ.get("PLAY_DEVICE_LIMIT", "3")))
    except ValueError: return 3
def grace_days():
    try: return max(0, int(os.environ.get("PLAY_SUB_GRACE_DAYS", "3")))
    except ValueError: return 3


class GoogleError(Exception):
    def __init__(self, status, text=""): super().__init__(f"{status} {text[:200]}"); self.status = status


class Google:
    """Minimal Google Play Developer API client (service account, RS256 JWT, no extra libraries)."""
    def __init__(self, keyfile):
        with open(keyfile, "r", encoding="utf-8") as f: self.k = json.load(f)
        self._tok = ""; self._exp = 0

    @staticmethod
    def _b64(b): return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

    def _token(self):
        if self._tok and time.time() < self._exp - 60: return self._tok
        t = int(time.time())
        head = self._b64(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
        claim = self._b64(json.dumps({"iss": self.k["client_email"], "scope": "https://www.googleapis.com/auth/androidpublisher",
                                      "aud": "https://oauth2.googleapis.com/token", "iat": t, "exp": t + 3000}).encode())
        key = serialization.load_pem_private_key(self.k["private_key"].encode(), None)
        sig = key.sign(f"{head}.{claim}".encode(), padding.PKCS1v15(), hashes.SHA256())
        r = httpx.post("https://oauth2.googleapis.com/token", timeout=15,
                       data={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": f"{head}.{claim}.{self._b64(sig)}"})
        if r.status_code != 200: raise GoogleError(r.status_code, r.text)
        self._tok = r.json()["access_token"]; self._exp = time.time() + int(r.json().get("expires_in", 3000))
        return self._tok

    def _call(self, method, path, **kw):
        r = httpx.request(method, f"{API}/{package()}/{path}", headers={"Authorization": "Bearer " + self._token()}, timeout=20, **kw)
        if r.status_code >= 400: raise GoogleError(r.status_code, r.text)
        return r.json() if r.content else {}

    def get_product(self, sku, token): return self._call("GET", f"purchases/products/{sku}/tokens/{token}")
    def ack_product(self, sku, token): return self._call("POST", f"purchases/products/{sku}/tokens/{token}:acknowledge", json={})
    def get_sub(self, token): return self._call("GET", f"purchases/subscriptionsv2/tokens/{token}")
    def ack_sub(self, sku, token): return self._call("POST", f"purchases/subscriptions/{sku}/tokens/{token}:acknowledge", json={})
    def voided(self, start_ms):
        out, page = [], ""
        while True:
            d = self._call("GET", "purchases/voidedpurchases", params={"startTime": str(start_ms), **({"token": page} if page else {})})
            out += d.get("voidedPurchases", [])
            page = (d.get("tokenPagination") or {}).get("nextPageToken", "")
            if not page: return out


def google():
    """The Google client, or None when no key is installed (dry run). Tests replace this function."""
    kf = os.environ.get("PLAY_KEY_FILE", "")
    if not kf or not os.path.isfile(kf): return None
    try: return Google(kf)
    except Exception as e:
        log.error("play key unreadable: %s", e); return None


def _date(ts): return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y%m%d")


def _fail(code, text): raise HTTPException(code, text)


def _check_product(g, token):
    """Returns ('ready'|'pending', info). Product and state come from Google's answer only."""
    try: p = g.get_product(SKU["pro"], token)
    except GoogleError as e:
        if e.status in (400, 404, 410): _fail(400, "This purchase was not recognised by Google Play.")
        raise
    if p.get("purchaseState") == 2: return "pending", {"ack": True}
    if p.get("purchaseState") != 0: _fail(400, "This purchase was cancelled or refunded.")
    return "ready", {"ack": p.get("acknowledgementState") == 1, "test": p.get("purchaseType") == 0, "linked": ""}


def _check_sub(g, token):
    try: s = g.get_sub(token)
    except GoogleError as e:
        if e.status in (400, 404, 410): _fail(400, "This subscription was not recognised by Google Play.")
        raise
    state = s.get("subscriptionState", "")
    if state == PENDING_SUB: return "pending", {}
    items = [i for i in s.get("lineItems", []) if i.get("productId") == SKU["sub"]]
    if not items: _fail(400, "This purchase is not a ServMod subscription.")
    if state not in OK_SUB_STATES: _fail(400, "This subscription is not active.")
    try: exp = datetime.datetime.fromisoformat(items[0]["expiryTime"].replace("Z", "+00:00")).timestamp()
    except Exception: _fail(502, "Google Play returned an unreadable subscription period.")
    if exp < time.time(): _fail(400, "This subscription has ended.")
    return "ready", {"ack": s.get("acknowledgementState") == "ACKNOWLEDGEMENT_STATE_ACKNOWLEDGED", "test": "testPurchase" in s,
                     "linked": s.get("linkedPurchaseToken", ""), "expiry": exp}


@router.post("/api/shop/play/redeem")
async def redeem(req: Request):
    try: d = await req.json()
    except Exception: d = {}
    d = d if isinstance(d, dict) else {}
    product = str(d.get("product", ""))
    token = str(d.get("purchase_token", "")).strip()
    dev = str(d.get("device_id", "")).strip().upper()
    if product not in SKU: _fail(400, "unknown product")
    if not core.DEVICE_RE.match(dev): _fail(400, "invalid device id")
    if not (20 <= len(token) <= 4096) or not re.match(r"^[\w.\-]+$", token): _fail(400, "invalid purchase token")
    if str(d.get("package", "")) != package(): _fail(400, "unknown package")
    from .app import ip
    if not core.rate_ok("play-ip:" + ip(req), 30, 3600) or not core.rate_ok("play-dev:" + dev, 12, 3600): _fail(429, "too many requests")
    g = google()
    if g is None: _fail(503, "Google Play checking is not configured on this server yet.")

    th = core.h(token)
    row = core.q("SELECT * FROM play_purchases WHERE token_hash=?", (th,)).fetchone()
    if row and row["voided"]: _fail(400, "This purchase was refunded.")
    try: state, info = (_check_product if product == "pro" else _check_sub)(g, token)
    except GoogleError as e:
        log.error("google check failed: %s", e); _fail(503, "Google Play could not be reached. Try again later.")
    if state == "pending": return {"status": "pending"}
    if info.get("test"): core.audit("play", "test-purchase", th[:12])

    # chain: all tokens of one subscription (resubscribe, upgrade) share one entitlement and one device limit
    chain = th
    if info.get("linked"):
        lr = core.q("SELECT chain FROM play_purchases WHERE token_hash=?", (core.h(info["linked"]),)).fetchone()
        chain = lr["chain"] if lr else core.h(info["linked"])
    ch_row = core.q("SELECT * FROM play_purchases WHERE chain=? ORDER BY created LIMIT 1", (chain,)).fetchone()
    if ch_row and ch_row["voided"]: _fail(400, "This purchase was refunded.")

    # acknowledge BEFORE any code is returned; if it fails nothing is issued
    if not info.get("ack"):
        try: (g.ack_product(SKU["pro"], token) if product == "pro" else g.ack_sub(SKU["sub"], token))
        except GoogleError as e:
            log.error("acknowledge failed: %s", e); _fail(503, "Google Play could not confirm the purchase. Try again later.")

    feats = "PRO" if product == "pro" else "SUB:" + _date(info["expiry"] + grace_days() * 86400)
    email = f"play-{chain[:24]}@play.invalid"
    u = core._user_for(email)
    ent = core.q("SELECT * FROM entitlements WHERE user_id=? AND source='play' AND revoked=0 ORDER BY id LIMIT 1", (u["id"],)).fetchone()
    if ent:
        if product == "sub":  # a later period moves the date forward, never back
            old = re.search(r"SUB:(\d{8})", ent["features"] or "")
            if not old or old.group(1) < feats[4:]: core.q("UPDATE entitlements SET features=? WHERE id=?", (feats, ent["id"]))
    else:
        core.q("INSERT INTO entitlements(user_id,product,features,seats,source,created) VALUES(?,?,?,?,?,?)",
               (u["id"], "servmod", feats, device_limit(), "play", core.now()))
    if not row:
        core.q("INSERT INTO play_purchases(token_hash,chain,product,created,voided) VALUES(?,?,?,?,0)", (th, chain, product, core.now()))
    try: code = issuing.issue(u, dev, "play")
    except HTTPException as e:
        if e.status_code == 409: _fail(409, f"This purchase is already used on {device_limit()} devices. Contact support@servmod.com to add more.")
        raise
    core.audit("play", "redeem", f"{th[:12]}:{product}:{dev}")
    return {"status": "ready", "code": code}


# ---------- refunds: Voided Purchases API, once a day
def run_voided_check(g=None, since_days=30):
    g = g or google()
    if g is None: return 0
    n = 0
    for v in g.voided(int((time.time() - since_days * 86400) * 1000)):
        th = core.h(str(v.get("purchaseToken", "")))
        row = core.q("SELECT * FROM play_purchases WHERE token_hash=?", (th,)).fetchone()
        if not row or row["voided"]: continue
        core.q("UPDATE play_purchases SET voided=1 WHERE chain=?", (row["chain"],))
        u = core.q("SELECT id FROM users WHERE email=?", (f"play-{row['chain'][:24]}@play.invalid",)).fetchone()
        if u: core.q("UPDATE entitlements SET revoked=1 WHERE user_id=? AND source='play'", (u["id"],))
        core.audit("play", "voided", th[:12]); n += 1
    return n


def start_worker():
    """Daily Voided Purchases check; does nothing when no key is installed."""
    if google() is None: return
    def loop():
        while True:
            try: run_voided_check()
            except Exception as e: log.error("voided check failed: %s", e)
            time.sleep(86400)
    threading.Thread(target=loop, daemon=True, name="play-voided").start()
