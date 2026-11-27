import os, json, logging, secrets, threading, time, re
from urllib.parse import urlparse
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from . import core, mail, licence, issuing, shop, box, chat, playbilling

log = logging.getLogger("servmod")
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
COOKIE = "sm_session"
DEFAULT_FEATURES = lambda: os.environ.get("DEFAULT_FEATURES", "ALL")

def ip(req: Request) -> str:
    return req.headers.get("x-real-ip") or (req.client.host if req.client else "?")

@app.middleware("http")
async def security(request: Request, call_next):
    if request.method not in ("GET", "HEAD", "OPTIONS") and not request.url.path.startswith("/api/pay/"):  # /api/pay/* is signed by the provider
        origin = request.headers.get("origin")
        ok_origin = origin is None or origin.rstrip("/") == core.SITE_URL.rstrip("/")
        if request.headers.get("x-requested-with") != "servmod" or not ok_origin:
            return JSONResponse({"error": "forbidden"}, 403)
    resp = await call_next(request)
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp

async def body(req: Request) -> dict:
    try:
        d = await req.json()
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}

def current(req: Request):
    u = core.session_user(req.cookies.get(COOKIE))
    if not u: raise HTTPException(401, "not signed in")
    return u

def admin(req: Request):
    u = current(req)
    if u["email"] not in core.ADMIN_EMAILS: raise HTTPException(403, "forbidden")
    return u

def set_cookie(resp: Response, tok: str):
    resp.set_cookie(COOKIE, tok, max_age=core.SESSION_DAYS * 86400, httponly=True, secure=os.environ.get("INSECURE_COOKIE") != "1", samesite="lax", path="/")

@app.get("/api/health")
def health(): return {"ok": True}

@app.get("/api/latest.apk")
def latest_apk():
    """Redirect to the newest stable APK named in the published feed."""
    try:
        with open(os.environ.get("FEED_DIR", "/var/www/servmod/servmod") + "/version.json", encoding="utf-8") as f:
            url = json.load(f)["apkUrl"]
    except Exception:
        # feed file not readable by this service (permissions): ask the public feed instead
        try:
            import urllib.request
            rq = urllib.request.Request(core.SITE_URL + "/servmod/version.json", headers={"User-Agent": "ServMod-API/1.0"})
            with urllib.request.urlopen(rq, timeout=5) as r:
                url = json.load(r)["apkUrl"]
        except Exception as e:
            logging.getLogger("servmod").warning("latest.apk: feed unreadable: %r", e)
            raise HTTPException(404, "no release published")
    if not url.startswith(core.SITE_URL + "/servmod/releases/"): raise HTTPException(404, "no release published")
    return RedirectResponse(url, 302)

# ---------- auth
@app.post("/api/auth/request")
async def auth_request(req: Request):
    d = await body(req)
    email = core.norm_email(d.get("email"))
    generic = {"ok": True}  # same answer whether or not account exists
    if not email: raise HTTPException(400, "invalid email")
    if not core.rate_ok("login-ip:" + ip(req), 10, 3600) or not core.rate_ok("login-em:" + email, 5, 3600):
        raise HTTPException(429, "too many requests, try later")
    link, code = core.create_login(email)
    url = f"{core.SITE_URL}/account/#t={link}"
    mail.send(email, "Your ServMod sign-in",
              f"Sign in to ServMod:\n\n{url}\n\nOr enter this code: {code}\n\nValid for 15 minutes. If you did not ask for this, ignore this e-mail.\n")
    return generic

def _login_response(u):
    tok = core.new_session(u["id"])
    r = JSONResponse({"ok": True, "email": u["email"]})
    set_cookie(r, tok)
    core.audit(u["email"], "login")
    return r

@app.post("/api/auth/verify")
async def auth_verify(req: Request):
    d = await body(req)
    if not core.rate_ok("verify-ip:" + ip(req), 30, 3600):
        raise HTTPException(429, "too many attempts")
    u = None
    if d.get("token"):
        u = core.consume_link(str(d["token"]))
    else:
        email = core.norm_email(d.get("email"))
        if email: u = core.consume_code(email, str(d.get("code", "")))
    if not u: raise HTTPException(400, "invalid or expired code")
    return _login_response(u)

@app.post("/api/auth/logout")
async def logout(req: Request):
    core.end_session(req.cookies.get(COOKIE))
    r = JSONResponse({"ok": True}); r.delete_cookie(COOKIE, path="/"); return r

# ---------- account
def licences_of(uid):
    rows = core.q("""SELECT l.id,l.device_id,l.label,l.code,l.created,l.released,l.entitlement_id
                     FROM licences l JOIN entitlements e ON e.id=l.entitlement_id WHERE e.user_id=? ORDER BY l.id""", (uid,)).fetchall()
    return [dict(r) for r in rows]

def moves_used(ent_id):
    return core.q("SELECT COUNT(*) c FROM licences WHERE entitlement_id=? AND released>?", (ent_id, core.now() - 365 * 86400)).fetchone()["c"]

@app.get("/api/me")
def me(req: Request):
    u = current(req)
    ents = []
    for e in core.q("SELECT * FROM entitlements WHERE user_id=? ORDER BY id", (u["id"],)).fetchall():
        active = core.q("SELECT COUNT(*) c FROM licences WHERE entitlement_id=? AND released IS NULL", (e["id"],)).fetchone()["c"]
        ents.append({"id": e["id"], "product": e["product"], "features": e["features"], "seats": e["seats"], "seats_used": active,
                     "moves_left": max(0, core.MOVES_PER_YEAR - moves_used(e["id"])), "revoked": bool(e["revoked"]), "created": e["created"]})
    return {"email": u["email"], "admin": u["email"] in core.ADMIN_EMAILS, "entitlements": ents, "licences": licences_of(u["id"])}

@app.post("/api/devices")
async def add_device(req: Request):
    u = current(req); d = await body(req)
    dev = str(d.get("device_id", "")).strip().upper()
    label = str(d.get("label", ""))[:60]
    if not core.DEVICE_RE.match(dev): raise HTTPException(400, "invalid Device ID")
    if not core.rate_ok("dev:" + str(u["id"]), 20, 3600): raise HTTPException(429, "too many requests")
    return {"code": issuing.issue(u, dev, label), "device_id": dev}

@app.post("/api/devices/release")
async def release_device(req: Request):
    u = current(req); d = await body(req)
    r = core.q("""SELECT l.id,l.entitlement_id FROM licences l JOIN entitlements e ON e.id=l.entitlement_id
                  WHERE l.id=? AND e.user_id=? AND l.released IS NULL""", (d.get("id"), u["id"])).fetchone()
    if not r: raise HTTPException(404, "not found")
    if moves_used(r["entitlement_id"]) >= core.MOVES_PER_YEAR: raise HTTPException(409, "device move limit reached; contact support")
    core.q("UPDATE licences SET released=? WHERE id=?", (core.now(), r["id"]))
    core.audit(u["email"], "release", str(r["id"]))
    return {"ok": True}

@app.get("/api/me/export")
def export(req: Request):
    u = current(req)
    return {"user": {"email": u["email"], "created": u["created"]}, "licences": licences_of(u["id"]),
            "tickets": [dict(t) for t in core.q("SELECT id,created,subject,message,status FROM tickets WHERE user_id=?", (u["id"],)).fetchall()]}

@app.delete("/api/me")
async def delete_me(req: Request):
    u = current(req)
    core.q("DELETE FROM licences WHERE entitlement_id IN (SELECT id FROM entitlements WHERE user_id=?)", (u["id"],))
    for t in ("entitlements", "sessions"): core.q(f"DELETE FROM {t} WHERE user_id=?", (u["id"],))
    core.q("UPDATE tickets SET user_id=NULL WHERE user_id=?", (u["id"],))
    core.q("DELETE FROM users WHERE id=?", (u["id"],))
    core.audit(u["email"], "delete_account")
    r = JSONResponse({"ok": True}); r.delete_cookie(COOKIE, path="/"); return r

# ---------- support
@app.post("/api/support")
async def support(req: Request):
    d = await body(req)
    if d.get("website"): return {"ok": True}  # honeypot
    email = core.norm_email(d.get("email"))
    msg = str(d.get("message", "")).strip()
    subj = str(d.get("subject", d.get("topic", "")))[:120]
    if not email or len(msg) < 10 or len(msg) > 5000: raise HTTPException(400, "please give a valid e-mail and a message (10+ characters)")
    if not core.rate_ok("sup-ip:" + ip(req), 5, 3600) or not core.rate_ok("sup-em:" + email, 5, 86400):
        raise HTTPException(429, "too many requests, try later")
    u = core.session_user(req.cookies.get(COOKIE))
    core.q("INSERT INTO tickets(created,user_id,email,subject,message) VALUES(?,?,?,?,?)", (core.now(), u["id"] if u else None, email, subj, msg))
    extra = "".join(f"{k}: {str(d.get(k))[:200]}\n" for k in ("name", "info") if d.get(k))
    to = os.environ.get("SUPPORT_TO") or (sorted(core.ADMIN_EMAILS)[0] if core.ADMIN_EMAILS else None)
    if to: mail.send(to, "[ServMod support] " + (subj or "new message"), f"From: {email}\n{extra}\n{msg}", reply_to=email)
    return {"ok": True}


# ---------- feature / device requests ("tell us what you need")
REQ_KINDS = {"device", "protocol", "feature", "other"}

@app.post("/api/requests")
async def request_idea(req: Request):
    d = await body(req)
    if d.get("website"): return {"ok": True}  # honeypot
    kind = str(d.get("kind", "device")).lower()
    if kind not in REQ_KINDS: kind = "other"
    device = str(d.get("device", "")).strip()[:120]
    protocol = str(d.get("protocol", "")).strip()[:120]
    connection = str(d.get("connection", "")).strip()[:120]
    details = str(d.get("details", "")).strip()[:3000]
    email_raw = str(d.get("email", "")).strip()
    email = core.norm_email(email_raw) if email_raw else None
    if email_raw and not email: raise HTTPException(400, "invalid email")
    if len(device) < 2: raise HTTPException(400, "please say which device, protocol or feature you need")
    if not core.rate_ok("req-ip:" + ip(req), 10, 3600) or (email and not core.rate_ok("req-em:" + email, 10, 86400)):
        raise HTTPException(429, "too many requests, try later")
    core.q("INSERT INTO requests(created,email,kind,device,protocol,connection,details) VALUES(?,?,?,?,?,?,?)",
           (core.now(), email, kind, device, protocol, connection, details))
    to = os.environ.get("SUPPORT_TO") or (sorted(core.ADMIN_EMAILS)[0] if core.ADMIN_EMAILS else None)
    if to:
        mail.send(to, f"[ServMod request] {kind}: {device}"[:150],
                  f"Kind: {kind}\nDevice / feature: {device}\nProtocol: {protocol or '-'}\nConnection: {connection or '-'}\nFrom: {email or '(no e-mail given)'}\n\n{details}",
                  reply_to=email)
    return {"ok": True}

# ---------- admin
BOT = re.compile(r"bot|crawl|spider|slurp|preview|headless|python|curl|wget|monitor|uptime|lighthouse|facebookexternalhit", re.I)

@app.post("/api/hit")
async def hit(req: Request):
    """Cookie-free visit counter. Stores no IP: the visitor id is a hash of IP+browser+day, so it cannot be followed across days."""
    ua = req.headers.get("user-agent", "")
    if not ua or BOT.search(ua): return {"ok": True}
    vip = req.headers.get("cf-connecting-ip") or ip(req)
    if not core.rate_ok("hit-" + vip, 400, 3600): return {"ok": True}
    d = await body(req)
    path = str(d.get("p") or "/")[:80]
    if not path.startswith("/") or "?" in path or "#" in path: path = path.split("?")[0].split("#")[0] or "/"
    ev = "download" if d.get("e") == "download" else "view"
    ref = ""
    try:
        host = (urlparse(str(d.get("r") or "")).hostname or "").lower()
        if host and host != urlparse(core.SITE_URL).hostname: ref = host[:60]
    except Exception: pass
    t = core.now(); day = time.strftime("%Y-%m-%d", time.gmtime(t))
    vid = core.h(f"{day}|{vip}|{ua}")[:16]
    core.q("INSERT INTO hits(ts,day,path,ev,vid,ref) VALUES(?,?,?,?,?,?)", (t, day, path, ev, vid, ref or None))
    if t % 50 == 0: core.q("DELETE FROM hits WHERE ts<?", (t - 400 * 86400,))
    return {"ok": True}

def visit_stats():
    t = core.now(); today = time.strftime("%Y-%m-%d", time.gmtime(t))
    days = [time.strftime("%Y-%m-%d", time.gmtime(t - i * 86400)) for i in range(13, -1, -1)]
    rows = {r["day"]: r for r in core.q("SELECT day, SUM(ev='view') v, COUNT(DISTINCT CASE WHEN ev='view' THEN vid END) u, SUM(ev='download') d FROM hits WHERE day>=? GROUP BY day", (days[0],)).fetchall()}
    daily = [{"day": x, "views": (rows[x]["v"] or 0) if x in rows else 0, "visitors": (rows[x]["u"] or 0) if x in rows else 0, "downloads": (rows[x]["d"] or 0) if x in rows else 0} for x in days]
    d7 = time.strftime("%Y-%m-%d", time.gmtime(t - 6 * 86400)); d30 = time.strftime("%Y-%m-%d", time.gmtime(t - 29 * 86400))
    def tot(since):
        r = core.q("SELECT COALESCE(SUM(ev='view'),0) v, COUNT(DISTINCT CASE WHEN ev='view' THEN vid END) u, COALESCE(SUM(ev='download'),0) d FROM hits WHERE day>=?", (since,)).fetchone()
        return {"views": r["v"], "visitors": r["u"], "downloads": r["d"]}
    return {"since": (core.q("SELECT MIN(day) m FROM hits").fetchone()["m"]), "today": tot(today), "d7": tot(d7), "d30": tot(d30), "daily": daily,
            "pages": [dict(r) for r in core.q("SELECT path, COUNT(*) n FROM hits WHERE ev='view' AND day>=? GROUP BY path ORDER BY n DESC LIMIT 12", (d30,)).fetchall()],
            "refs": [dict(r) for r in core.q("SELECT ref, COUNT(*) n FROM hits WHERE ev='view' AND ref IS NOT NULL AND day>=? GROUP BY ref ORDER BY n DESC LIMIT 8", (d30,)).fetchall()]}

@app.get("/api/admin/overview")
def overview(req: Request):
    admin(req)
    return {"visits": visit_stats(),
            "tickets": [dict(r) for r in core.q("SELECT * FROM tickets ORDER BY id DESC LIMIT 200")],
            "requests": [dict(r) for r in core.q("SELECT * FROM requests ORDER BY id DESC LIMIT 300")]}

# Licence groups (folders) in the admin panel. Search matches: e-mail, play-<id> (the Google Play purchase id), Device ID, phone label,
# the first characters of a Play purchase hash (as shown in the audit log), an order id, or the licence number.
_GROUPS = {"all": "1=1", "shop": "e.source='shop' AND e.revoked=0", "play": "e.source='play' AND e.revoked=0",
           "admin": "e.source LIKE 'admin:%' AND e.revoked=0", "revoked": "e.revoked=1"}

def _ent_search(q):
    if not q: return "1=1", []
    like = "%" + q + "%"
    return ("(lower(u.email) LIKE ? OR EXISTS(SELECT 1 FROM licences l WHERE l.entitlement_id=e.id AND (lower(l.device_id) LIKE ? OR lower(COALESCE(l.label,'')) LIKE ?))"
            " OR EXISTS(SELECT 1 FROM play_purchases p WHERE lower(p.token_hash) LIKE ? AND u.email='play-'||substr(p.chain,1,24)||'@play.invalid')"
            " OR EXISTS(SELECT 1 FROM orders o WHERE lower(o.email)=lower(u.email) AND lower(o.ext_id) LIKE ?)"
            " OR CAST(e.id AS TEXT)=?)", [like, like, like, q + "%", like, q.lstrip("#")])

@app.get("/api/admin/licences")
def admin_licences(req: Request, q: str = "", group: str = "all", offset: int = 0, limit: int = 25):
    admin(req)
    q = re.sub(r"[%_\\]", "", q.strip().lower())[:100]
    limit = max(1, min(limit, 50)); offset = max(0, offset)
    sc, sp = _ent_search(q)
    cr = core.q(f"SELECT COALESCE(SUM(e.source='shop' AND e.revoked=0),0) shop, COALESCE(SUM(e.source='play' AND e.revoked=0),0) play, "
                f"COALESCE(SUM(e.source LIKE 'admin:%' AND e.revoked=0),0) admin, COALESCE(SUM(e.revoked=1),0) revoked, COUNT(*) \"all\" "
                f"FROM entitlements e JOIN users u ON u.id=e.user_id WHERE {sc}", sp).fetchone()
    nolic = "NOT EXISTS(SELECT 1 FROM entitlements e WHERE e.user_id=u.id)"
    acc_where, acc_p = (nolic + " AND lower(u.email) LIKE ?", ["%" + q + "%"]) if q else (nolic, [])
    counts = dict(cr); counts["accounts"] = core.q(f"SELECT COUNT(*) c FROM users u WHERE {acc_where}", acc_p).fetchone()["c"]
    if group == "accounts":
        rows = core.q(f"SELECT u.id,u.email,u.created,u.last_login FROM users u WHERE {acc_where} ORDER BY u.id DESC LIMIT ? OFFSET ?", acc_p + [limit + 1, offset]).fetchall()
        return {"counts": counts, "items": [dict(r, kind="account", protected=r["email"] in core.ADMIN_EMAILS) for r in rows[:limit]], "more": len(rows) > limit}
    if group not in _GROUPS: group = "all"
    rows = core.q(f"SELECT e.id,e.features,e.seats,e.source,e.created,e.revoked,u.email FROM entitlements e JOIN users u ON u.id=e.user_id "
                  f"WHERE {_GROUPS[group]} AND {sc} ORDER BY e.id DESC LIMIT ? OFFSET ?", sp + [limit + 1, offset]).fetchall()
    items = []
    for r in rows[:limit]:
        it = dict(r, kind="licence")
        it["devices"] = [dict(x) for x in core.q("SELECT device_id,label,created,released FROM licences WHERE entitlement_id=? ORDER BY id", (r["id"],)).fetchall()]
        it["orders"] = [dict(x) for x in core.q("SELECT provider,product,pence,created FROM orders WHERE lower(email)=lower(?) ORDER BY id", (r["email"],)).fetchall()] if r["source"] == "shop" else []
        it["test"] = r["email"].lower().endswith("@example.com") or "@personal.example.com" in r["email"].lower()
        items.append(it)
    return {"counts": counts, "items": items, "more": len(rows) > limit}

def _drop_user_if_empty(uid, me):
    u = core.q("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if not u or u["email"] in core.ADMIN_EMAILS or u["id"] == me["id"]: return False
    if core.q("SELECT 1 FROM entitlements WHERE user_id=?", (uid,)).fetchone(): return False
    core.q("DELETE FROM sessions WHERE user_id=?", (uid,)); core.q("DELETE FROM login_tokens WHERE email=?", (u["email"],))
    core.q("DELETE FROM users WHERE id=?", (uid,))
    return True

@app.post("/api/admin/purge")
async def purge(req: Request):
    """Removes junk from the panel. Only a REVOKED licence (with its phones) or an account that has no licence can be removed.
    Orders stay in the database (accounting); the audit log keeps a line."""
    a = admin(req); d = await body(req)
    if d.get("id") is not None:
        e = core.q("SELECT * FROM entitlements WHERE id=?", (d.get("id"),)).fetchone()
        if not e: raise HTTPException(404, "no such licence")
        if not e["revoked"]: raise HTTPException(409, "revoke it first")
        core.q("DELETE FROM licences WHERE entitlement_id=?", (e["id"],)); core.q("DELETE FROM entitlements WHERE id=?", (e["id"],))
        core.audit(a["email"], "purge-licence", str(e["id"]))
        _drop_user_if_empty(e["user_id"], a)
        return {"ok": True}
    try: uid = int(d.get("user_id"))
    except (TypeError, ValueError): raise HTTPException(400, "bad request")
    if not _drop_user_if_empty(uid, a): raise HTTPException(409, "this account cannot be removed (it has a licence, or it is yours or an admin)")
    core.audit(a["email"], "purge-account", str(uid))
    return {"ok": True}

@app.post("/api/admin/grant")
async def grant(req: Request):
    a = admin(req); d = await body(req)
    email = core.norm_email(d.get("email"))
    if not email: raise HTTPException(400, "invalid email")
    u = core._user_for(email)
    seats = max(1, min(int(d.get("seats", 1) or 1), 20))
    core.q("INSERT INTO entitlements(user_id,product,features,seats,source,created) VALUES(?,?,?,?,?,?)",
           (u["id"], "servmod", str(d.get("features") or DEFAULT_FEATURES())[:200], seats, "admin:" + a["email"], core.now()))
    core.audit(a["email"], "grant", email)
    return {"ok": True}

@app.post("/api/admin/revoke")
async def revoke(req: Request):
    a = admin(req); d = await body(req)
    core.q("UPDATE entitlements SET revoked=1 WHERE id=?", (d.get("id"),))
    core.audit(a["email"], "revoke", str(d.get("id")))
    return {"ok": True}

@app.post("/api/admin/ticket")
async def ticket(req: Request):
    admin(req); d = await body(req)
    core.q("UPDATE tickets SET status=? WHERE id=?", ("closed" if d.get("status") == "closed" else "open", d.get("id")))
    return {"ok": True}

@app.post("/api/admin/request")
async def request_status(req: Request):
    admin(req); d = await body(req)
    st = d.get("status") if d.get("status") in ("new", "planned", "done", "declined") else "new"
    core.q("UPDATE requests SET status=? WHERE id=?", (st, d.get("id")))
    return {"ok": True}

app.include_router(shop.router)
app.include_router(box.router)
app.include_router(chat.router)
app.include_router(playbilling.router)

@app.on_event("startup")
def _play_worker(): playbilling.start_worker()
