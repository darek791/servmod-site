import os, json, logging, secrets, threading, time
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from . import core, mail, licence, issuing, shop

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
    wl = core.q("SELECT 1 FROM waitlist WHERE email=? AND confirmed=1", (u["email"],)).fetchone()
    return {"email": u["email"], "admin": u["email"] in core.ADMIN_EMAILS, "entitlements": ents, "licences": licences_of(u["id"]), "waitlist": bool(wl)}

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
            "tickets": [dict(t) for t in core.q("SELECT id,created,subject,message,status FROM tickets WHERE user_id=?", (u["id"],)).fetchall()],
            "waiting_list": [dict(t) for t in core.q("SELECT created,confirmed,source FROM waitlist WHERE email=?", (u["email"],)).fetchall()]}

@app.delete("/api/me")
async def delete_me(req: Request):
    u = current(req)
    core.q("DELETE FROM licences WHERE entitlement_id IN (SELECT id FROM entitlements WHERE user_id=?)", (u["id"],))
    for t in ("entitlements", "sessions"): core.q(f"DELETE FROM {t} WHERE user_id=?", (u["id"],))
    core.q("UPDATE tickets SET user_id=NULL WHERE user_id=?", (u["id"],))
    core.q("DELETE FROM waitlist WHERE email=?", (u["email"],))
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


# ---------- waiting list (double opt-in; confirm/unsubscribe links carry a token in the URL fragment and are completed by a POST,
# so mail scanners that pre-open links cannot confirm or unsubscribe anyone by accident)
WL_FOOT = "\n\n--\nYou get this e-mail because you joined the ServMod waiting list. Unsubscribe: {url}\n"

def _wl_url(kind, tok): return f"{core.SITE_URL}/waitlist.html#{kind}={tok}"

@app.post("/api/waitlist")
async def waitlist_join(req: Request):
    d = await body(req)
    if d.get("website"): return {"ok": True}  # honeypot
    email = core.norm_email(d.get("email"))
    if not email: raise HTTPException(400, "invalid email")
    if not core.rate_ok("wl-ip:" + ip(req), 8, 3600) or not core.rate_ok("wl-em:" + email, 3, 86400):
        raise HTTPException(429, "too many requests, try later")
    row = core.q("SELECT * FROM waitlist WHERE email=?", (email,)).fetchone()
    if row and row["confirmed"]: return {"ok": True}  # same answer, nothing sent
    tok = row["tok"] if row else secrets.token_urlsafe(24)
    if not row: core.q("INSERT INTO waitlist(email,created,tok,source) VALUES(?,?,?,?)", (email, core.now(), tok, "web"))
    mail.send(email, "Confirm your place on the ServMod waiting list",
              f"Someone (hopefully you) asked to be told when the first public version of ServMod is released.\n\nConfirm here:\n{_wl_url('confirm', tok)}\n\n"
              "If it was not you, ignore this e-mail and nothing will happen. We send one e-mail when ServMod is released, and nothing else.\n")
    return {"ok": True}

@app.post("/api/waitlist/confirm")
async def waitlist_confirm(req: Request):
    d = await body(req)
    if not core.rate_ok("wlc-ip:" + ip(req), 30, 3600): raise HTTPException(429, "too many attempts")
    r = core.q("UPDATE waitlist SET confirmed=1 WHERE tok=?", (str(d.get("token", ""))[:80],))
    if r.rowcount < 1: raise HTTPException(400, "invalid or expired link")
    return {"ok": True}

@app.post("/api/waitlist/unsubscribe")
async def waitlist_unsub(req: Request):
    d = await body(req)
    if not core.rate_ok("wlu-ip:" + ip(req), 30, 3600): raise HTTPException(429, "too many attempts")
    r = core.q("DELETE FROM waitlist WHERE tok=?", (str(d.get("token", ""))[:80],))
    if r.rowcount < 1: raise HTTPException(400, "invalid link")
    return {"ok": True}

@app.post("/api/waitlist/me")
async def waitlist_me(req: Request):
    u = current(req); d = await body(req)
    if d.get("on"):
        if core.q("SELECT 1 FROM waitlist WHERE email=?", (u["email"],)).fetchone():
            core.q("UPDATE waitlist SET confirmed=1 WHERE email=?", (u["email"],))
        else:  # the sign-in already proved the address, so no second confirmation is needed
            core.q("INSERT INTO waitlist(email,created,confirmed,tok,source) VALUES(?,?,1,?,?)", (u["email"], core.now(), secrets.token_urlsafe(24), "account"))
    else:
        core.q("DELETE FROM waitlist WHERE email=?", (u["email"],))
    return {"ok": True, "on": bool(d.get("on"))}

def _wl_send_all(rows, subject, text):
    for r in rows:
        if mail.send(r["email"], subject, text + WL_FOOT.format(url=_wl_url("unsub", r["tok"]))):
            core.q("UPDATE waitlist SET notified=? WHERE id=?", (core.now(), r["id"]))
        time.sleep(0.6)  # stay under the mail provider's rate limit

@app.post("/api/admin/waitlist/notify")
async def waitlist_notify(req: Request):
    a = admin(req); d = await body(req)
    subject = str(d.get("subject", "")).strip()[:150]; text = str(d.get("text", "")).strip()
    if not subject or len(text) < 10 or len(text) > 8000: raise HTTPException(400, "subject and a message of 10-8000 characters are needed")
    if d.get("test"):
        mail.send(a["email"], "[TEST] " + subject, text + WL_FOOT.format(url=_wl_url("unsub", "test-token")))
        return {"ok": True, "test": True}
    if d.get("confirm") is not True: raise HTTPException(400, "confirmation missing")
    sql = "SELECT * FROM waitlist WHERE confirmed=1" + ("" if d.get("again") else " AND notified IS NULL")
    rows = [dict(r) for r in core.q(sql).fetchall()]
    core.audit(a["email"], "waitlist_notify", f"{len(rows)} recipients: {subject}")
    if rows: threading.Thread(target=_wl_send_all, args=(rows, subject, text), daemon=True).start()
    return {"ok": True, "queued": len(rows)}


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
@app.get("/api/admin/overview")
def overview(req: Request):
    admin(req)
    return {"users": [dict(r) for r in core.q("SELECT id,email,created,last_login FROM users ORDER BY id DESC LIMIT 200")],
            "tickets": [dict(r) for r in core.q("SELECT * FROM tickets ORDER BY id DESC LIMIT 200")],
            "requests": [dict(r) for r in core.q("SELECT * FROM requests ORDER BY id DESC LIMIT 300")],
            "entitlements": [dict(r) for r in core.q("SELECT e.*,u.email FROM entitlements e JOIN users u ON u.id=e.user_id ORDER BY e.id DESC LIMIT 200")],
            "waitlist": {"confirmed": core.q("SELECT COUNT(*) c FROM waitlist WHERE confirmed=1").fetchone()["c"],
                         "pending": core.q("SELECT COUNT(*) c FROM waitlist WHERE confirmed=0").fetchone()["c"],
                         "not_yet_notified": core.q("SELECT COUNT(*) c FROM waitlist WHERE confirmed=1 AND notified IS NULL").fetchone()["c"],
                         "latest": [dict(r) for r in core.q("SELECT email,created,confirmed,source,notified FROM waitlist ORDER BY id DESC LIMIT 100")]}}

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
