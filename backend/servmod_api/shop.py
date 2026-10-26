"""Shop: Stripe Checkout + signed webhook -> entitlement -> activation code by e-mail.
Closed by default: nothing is sold until STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET are set (see /etc/servmod/pay.env).
Prices come from the environment (pence), so they can change without a release."""
import hashlib, hmac, json, logging, os, re, time
import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from . import core, mail, issuing

log = logging.getLogger("servmod.shop")
router = APIRouter()

def _pence(name, default): 
    try: return int(os.environ.get(name, default))
    except ValueError: return default

def products():
    return {
        "pro": {"name": "ServMod Pro (one-time)", "pence": _pence("PRICE_PRO_PENCE", 4000)},
        "sub": {"name": "ServMod Subscription (1 year)", "pence": _pence("PRICE_SUB_PENCE", 2000)},
    }

def stripe_on():
    return bool(os.environ.get("STRIPE_SECRET_KEY") and os.environ.get("STRIPE_WEBHOOK_SECRET"))

def paypal_on():
    return bool(os.environ.get("PAYPAL_CLIENT_ID") and os.environ.get("PAYPAL_SECRET"))

def is_open():
    return stripe_on() or paypal_on()

def _fmt(p): return f"£{p / 100:.2f}".replace(".00", "")

@router.get("/api/shop/config")
def config():
    return {"open": is_open(), "stripe": stripe_on(), "paypal": paypal_on(), "currency": "gbp", "products": {k: {"name": v["name"], "pence": v["pence"], "price": _fmt(v["pence"])} for k, v in products().items()}}

# ---------- fulfilment (provider independent, idempotent)
def _sub_date(existing_features, now):
    m = re.search(r"SUB:(\d{8})", existing_features or "")
    base = now
    if m:
        import datetime
        try:
            cur = datetime.datetime.strptime(m.group(1), "%Y%m%d").replace(tzinfo=datetime.timezone.utc).timestamp()
            base = max(now, cur)
        except ValueError: pass
    import datetime
    return (datetime.datetime.fromtimestamp(base, datetime.timezone.utc) + datetime.timedelta(days=365)).strftime("%Y%m%d")

def _features_after(old, product, now):
    parts = [p for p in (old or "").split(",") if p]
    if "ALL" in parts: return old
    if product == "pro":
        if "PRO" not in parts: parts.insert(0, "PRO")
    else:
        parts = [p for p in parts if not p.startswith("SUB:")] + ["SUB:" + _sub_date(old, now)]
    return ",".join(parts)

def fulfil(provider, ext_id, email, product, pence, currency="gbp", device_id="", claim=""):
    """Grant what was bought. Returns 'new', 'duplicate' or 'ignored'. Safe to call twice for the same payment."""
    email = core.norm_email(email)
    if not email or product not in products():
        core.audit("shop", "ignored", f"{provider}:{ext_id}:{email}:{product}"); return "ignored"
    if core.q("SELECT 1 FROM orders WHERE provider=? AND ext_id=?", (provider, ext_id)).fetchone(): return "duplicate"
    now = core.now(); u = core._user_for(email)
    ent = core.q("SELECT * FROM entitlements WHERE user_id=? AND source='shop' AND revoked=0 ORDER BY id LIMIT 1", (u["id"],)).fetchone()
    if ent:
        feats = _features_after(ent["features"], product, now)
        core.q("UPDATE entitlements SET features=? WHERE id=?", (feats, ent["id"]))
    else:
        feats = _features_after("", product, now)
        core.q("INSERT INTO entitlements(user_id,product,features,seats,source,created) VALUES(?,?,?,?,?,?)", (u["id"], "servmod", feats, 1, "shop", now))
    dev = (device_id or "").strip().upper()
    dev = dev if core.DEVICE_RE.match(dev) else ""
    core.q("INSERT INTO orders(provider,ext_id,email,product,pence,currency,created,device_id,note) VALUES(?,?,?,?,?,?,?,?,?)", (provider, ext_id, email, product, pence, currency, now, dev or None, ("claim:" + claim) if (claim and dev) else None))
    core.audit("shop", "order", f"{provider}:{ext_id}:{email}:{product}:{pence}")
    code = ""
    if dev:
        try: code = issuing.issue(u, dev, "bought")
        except Exception as e: log.error("auto-issue failed for %s: %s", email, getattr(e, "detail", e))
    _receipt(email, product, pence, feats, dev, code)
    return "new"

def _receipt(email, product, pence, feats, dev, code):
    what = products()[product]["name"]
    lines = [f"Thank you for buying {what} ({_fmt(pence)}).", ""]
    if code:
        lines += [f"Your activation code for Device ID {dev}:", "", code, "",
                  "In the app open Settings > Subscription, paste the code and tap Activate.", ""]
    else:
        lines += ["To get your activation code:", f"1. Open the app, Settings > Subscription, and copy the Device ID.",
                  f"2. Sign in at {core.SITE_URL}/account/ with this e-mail address ({email}).",
                  "3. Paste the Device ID, and the code appears on the page.", ""]
    if "SUB:" in feats and product == "sub":
        lines += ["If you already activated this phone, open your account page and tap Get code again to refresh it.", ""]
    lines += ["Questions: reply to this e-mail or write to support@servmod.com.", "", "ServMod"]
    mail.send(email, f"Your ServMod {'code' if code else 'licence'}", "\n".join(lines))

def _claim_hash(token):
    """The app sends a random secret per purchase; only its hash is stored."""
    import hashlib
    token = token.strip()
    return hashlib.sha256(token.encode()).hexdigest() if 16 <= len(token) <= 128 else ""

@router.get("/api/shop/claim")
def claim(request: Request, device: str = "", token: str = ""):
    """App polls this after payment. Returns the activation code once the order is paid; the code is bound to the Device ID."""
    from .app import ip
    if not core.rate_ok("cl:" + ip(request), 120, 3600): raise HTTPException(429, "too many requests")
    dev = device.strip().upper(); h = _claim_hash(token)
    if not core.DEVICE_RE.match(dev) or not h: raise HTTPException(400, "bad request")
    o = core.q("SELECT * FROM orders WHERE device_id=? AND note=? ORDER BY id DESC LIMIT 1", (dev, "claim:" + h)).fetchone()
    if not o: return {"status": "pending"}
    u = core._user_for(o["email"])
    try: code = issuing.issue(u, dev, "bought")
    except HTTPException as e: return {"status": "error", "detail": e.detail}
    return {"status": "ready", "code": code}

# ---------- PayPal (Orders v2: create -> buyer approves -> we capture on return -> fulfil)
def _pp_base():
    return "https://api-m.paypal.com" if os.environ.get("PAYPAL_ENV", "sandbox") == "live" else "https://api-m.sandbox.paypal.com"

def _pp_token():
    r = httpx.post(_pp_base() + "/v1/oauth2/token", data={"grant_type": "client_credentials"}, timeout=20,
                   auth=(os.environ["PAYPAL_CLIENT_ID"], os.environ["PAYPAL_SECRET"]))
    r.raise_for_status(); return r.json()["access_token"]

def _paypal_create(product, p, dev, claim):
    try:
        tok = _pp_token()
        body = {"intent": "CAPTURE", "purchase_units": [{"description": p["name"], "amount": {"currency_code": "GBP", "value": f"{p['pence'] / 100:.2f}"}}],
                "payment_source": {"paypal": {"experience_context": {"brand_name": "ServMod", "user_action": "PAY_NOW", "shipping_preference": "NO_SHIPPING",
                                  "return_url": f"{core.SITE_URL}/api/pay/paypal/return", "cancel_url": f"{core.SITE_URL}/pricing.html"}}}}
        r = httpx.post(_pp_base() + "/v2/checkout/orders", json=body, timeout=20, headers={"Authorization": "Bearer " + tok})
        r.raise_for_status(); o = r.json()
        url = next(l["href"] for l in o["links"] if l["rel"] in ("payer-action", "approve"))
    except Exception as e:
        log.error("paypal create failed: %s", e); raise HTTPException(502, "payment provider error, try again later")
    core.q("INSERT OR REPLACE INTO pending_orders(ext_id,provider,product,device_id,claim,created) VALUES(?,?,?,?,?,?)", (o["id"], "paypal", product, dev or None, claim or None, core.now()))
    return url

@router.get("/api/pay/paypal/return")
def paypal_return(token: str = ""):
    """PayPal sends the buyer here after approval. We capture the payment server side and only then fulfil."""
    p = core.q("SELECT * FROM pending_orders WHERE ext_id=? AND provider='paypal'", (token,)).fetchone() if token else None
    dest = f"{core.SITE_URL}/pricing.html"
    if not p: return RedirectResponse(dest)
    try:
        tok = _pp_token()
        r = httpx.post(f"{_pp_base()}/v2/checkout/orders/{token}/capture", timeout=30, headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"}, content=b"{}")
        o = r.json()
        if r.status_code == 422 and "ORDER_ALREADY_CAPTURED" in r.text:
            r = httpx.get(f"{_pp_base()}/v2/checkout/orders/{token}", timeout=20, headers={"Authorization": "Bearer " + tok}); o = r.json()
        elif r.status_code >= 400: raise RuntimeError(r.text[:200])
        cap = o["purchase_units"][0]["payments"]["captures"][0]
        if o.get("status") != "COMPLETED" or cap.get("status") != "COMPLETED": raise RuntimeError("not completed: %s/%s" % (o.get("status"), cap.get("status")))
        email = (o.get("payer") or {}).get("email_address", "")
        pence = int(round(float(cap["amount"]["value"]) * 100))
        if fulfil("paypal", token, email, p["product"], pence, "gbp", p["device_id"] or "", p["claim"] or "") == "ignored": raise RuntimeError("payment captured but not granted (no payer e-mail?)")
    except Exception as e:
        log.error("paypal capture failed for %s: %s", token, e)
        for a in core.ADMIN_EMAILS: mail.send(a, "ServMod: PayPal capture problem", f"Order {token}: {e}")
        return RedirectResponse(dest + "#paid=problem")
    core.q("DELETE FROM pending_orders WHERE ext_id=?", (token,))
    return RedirectResponse(dest + ("#paid=app" if p["device_id"] else "#paid=1"))

# ---------- Stripe
STRIPE = "https://api.stripe.com/v1"

@router.post("/api/shop/checkout")
async def checkout(req: Request):
    if not is_open(): raise HTTPException(503, "ordering is not open yet")
    try: d = await req.json()
    except Exception: d = {}
    d = d if isinstance(d, dict) else {}
    product = str(d.get("product", ""))
    P = products()
    if product not in P: raise HTTPException(400, "unknown product")
    provider = str(d.get("provider") or "stripe")
    if provider not in ("stripe", "paypal"): raise HTTPException(400, "unknown payment provider")
    if (provider == "paypal" and not paypal_on()) or (provider == "stripe" and not stripe_on()): raise HTTPException(503, "this payment method is not available")
    from .app import ip
    if not core.rate_ok("co:" + ip(req), 20, 3600): raise HTTPException(429, "too many requests")
    dev = str(d.get("device_id") or "").strip().upper()
    if dev and not core.DEVICE_RE.match(dev): raise HTTPException(400, "invalid Device ID")
    claim = _claim_hash(str(d.get("claim") or "")) if dev else ""
    if dev and not claim: raise HTTPException(400, "claim token required (16-128 characters)")
    if provider == "paypal": return {"url": _paypal_create(product, P[product], dev, claim)}
    form = {
        "mode": "payment", "success_url": f"{core.SITE_URL}/pricing.html#paid={'app' if dev else '1'}", "cancel_url": f"{core.SITE_URL}/pricing.html",
        "line_items[0][quantity]": "1", "line_items[0][price_data][currency]": "gbp",
        "line_items[0][price_data][unit_amount]": str(P[product]["pence"]),
        "line_items[0][price_data][product_data][name]": P[product]["name"],
        "metadata[product]": product, "payment_intent_data[metadata][product]": product,
        "custom_text[submit][message]": "By paying you accept the Terms of use and Refunds policy on servmod.com. You ask us to deliver your activation code at once and you accept that you then lose the 14-day right to cancel.",
    }
    if dev:
        form["metadata[device_id]"] = dev; form["metadata[claim]"] = claim
    else:
        form.update({"custom_fields[0][key]": "device_id", "custom_fields[0][type]": "text", "custom_fields[0][optional]": "true",
                     "custom_fields[0][label][type]": "custom", "custom_fields[0][label][custom]": "Device ID (optional)"})
    email = core.norm_email(d.get("email"))
    if email: form["customer_email"] = email
    try:
        r = httpx.post(STRIPE + "/checkout/sessions", data=form, timeout=20, headers={"Authorization": "Bearer " + os.environ["STRIPE_SECRET_KEY"]})
        r.raise_for_status(); url = r.json()["url"]
    except Exception as e:
        log.error("stripe checkout failed: %s", e); raise HTTPException(502, "payment provider error, try again later")
    return {"url": url}

def verify_stripe(payload: bytes, header: str, secret: str, tolerance=300, now=None):
    try:
        parts = dict(p.split("=", 1) for p in header.split(",") if "=" in p)
        t = int(parts["t"])
        sigs = [p.split("=", 1)[1] for p in header.split(",") if p.startswith("v1=")]
    except Exception: return False
    if abs((now or time.time()) - t) > tolerance: return False
    mac = hmac.new(secret.encode(), f"{t}.".encode() + payload, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(mac, s) for s in sigs)

@router.post("/api/pay/stripe")
async def stripe_webhook(req: Request):
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    raw = await req.body()
    if not secret or not verify_stripe(raw, req.headers.get("stripe-signature", ""), secret):
        raise HTTPException(400, "bad signature")
    ev = json.loads(raw)
    typ = ev.get("type", ""); obj = (ev.get("data") or {}).get("object") or {}
    if typ in ("checkout.session.completed", "checkout.session.async_payment_succeeded") and obj.get("payment_status") == "paid":
        cd = obj.get("customer_details") or {}
        md = obj.get("metadata") or {}
        dev = md.get("device_id") or ""
        for f in obj.get("custom_fields") or []:
            if f.get("key") == "device_id": dev = ((f.get("text") or {}).get("value")) or ""
        res = fulfil("stripe", obj.get("id", ""), cd.get("email") or obj.get("customer_email") or "", (obj.get("metadata") or {}).get("product", ""),
                     int(obj.get("amount_total") or 0), obj.get("currency") or "gbp", dev, md.get("claim") or "")
        return {"ok": True, "result": res}
    if typ in ("charge.refunded", "charge.dispute.created"):
        core.audit("stripe", typ, str(obj.get("id", "")))
        for a in core.ADMIN_EMAILS: mail.send(a, "ServMod: refund or dispute in Stripe", f"{typ} {obj.get('id','')}. Revoke the licence in the account admin panel if needed.")
    return {"ok": True}
