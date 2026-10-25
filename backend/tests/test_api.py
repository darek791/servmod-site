import os, re, pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient

H = {"X-Requested-With": "servmod"}

@pytest.fixture()
def c(tmp_path, monkeypatch):
    key = ec.generate_private_key(ec.SECP256R1())
    kp = tmp_path / "k.pem"
    kp.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    monkeypatch.setenv("LICENSE_KEY", str(kp)); monkeypatch.setenv("INSECURE_COOKIE", "1")
    from servmod_api import core, mail
    core.reset(str(tmp_path)); core.ADMIN_EMAILS = {"boss@x.com"}; mail.OUTBOX.clear()
    from servmod_api.app import app
    cl = TestClient(app, base_url="http://testserver"); cl.key = key
    return cl

def login(c, email):
    from servmod_api import mail
    assert c.post("/api/auth/request", json={"email": email}, headers=H).status_code == 200
    text = mail.OUTBOX[-1][2]
    return re.search(r"#t=(\S+)", text).group(1), re.search(r"code: (\d{6})", text).group(1)

def test_csrf_header_required(c):
    assert c.post("/api/auth/request", json={"email": "a@b.com"}).status_code == 403

def test_link_login_and_me(c):
    tok, _ = login(c, "a@b.com")
    assert c.get("/api/me").status_code == 401
    assert c.post("/api/auth/verify", json={"token": tok}, headers=H).status_code == 200
    assert c.get("/api/me").json()["email"] == "a@b.com"
    assert c.post("/api/auth/verify", json={"token": tok}, headers=H).status_code == 400  # single use

def test_code_login_and_bruteforce(c):
    _, code = login(c, "a@b.com")
    for _ in range(5):
        assert c.post("/api/auth/verify", json={"email": "a@b.com", "code": "000000" if code != "000000" else "111111"}, headers=H).status_code == 400
    assert c.post("/api/auth/verify", json={"email": "a@b.com", "code": code}, headers=H).status_code == 400  # locked out

def test_licence_flow(c):
    from servmod_api import licence
    tok, _ = login(c, "boss@x.com"); c.post("/api/auth/verify", json={"token": tok}, headers=H)
    assert c.post("/api/devices", json={"device_id": "ABCDEF123"}, headers=H).status_code == 402
    assert c.post("/api/admin/grant", json={"email": "boss@x.com"}, headers=H).status_code == 200
    r = c.post("/api/devices", json={"device_id": "abcdef123"}, headers=H).json()
    assert licence.verify_code(c.key.public_key(), r["code"])
    assert c.post("/api/devices", json={"device_id": "ABCDEF123"}, headers=H).json()["code"] == r["code"]
    assert c.post("/api/devices", json={"device_id": "OTHER-DEV1"}, headers=H).status_code == 409  # seat used
    lid = c.get("/api/me").json()["licences"][0]["id"]
    assert c.post("/api/devices/release", json={"id": lid}, headers=H).status_code == 200
    assert c.post("/api/devices", json={"device_id": "OTHER-DEV1"}, headers=H).status_code == 200
    assert c.post("/api/devices", json={"device_id": "bad id!"}, headers=H).status_code == 400

def test_admin_only(c):
    tok, _ = login(c, "a@b.com"); c.post("/api/auth/verify", json={"token": tok}, headers=H)
    assert c.get("/api/admin/overview").status_code == 403
    assert c.post("/api/admin/grant", json={"email": "a@b.com"}, headers=H).status_code == 403

def test_support_and_delete(c):
    from servmod_api import mail
    r = c.post("/api/support", json={"email": "a@b.com", "message": "hello there, help"}, headers=H)
    assert r.status_code == 200
    assert c.post("/api/support", json={"email": "a@b.com", "message": "short"}, headers=H).status_code == 400
    tok, _ = login(c, "a@b.com"); c.post("/api/auth/verify", json={"token": tok}, headers=H)
    assert c.delete("/api/me", headers=H).status_code == 200
    assert c.get("/api/me").status_code == 401

def test_hex_key_format_matches_vendor_script(tmp_path, monkeypatch):
    from servmod_api import licence
    d = 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
    kp = tmp_path / "license_private.key"; kp.write_text("%064x\n" % d)
    monkeypatch.setenv("LICENSE_KEY", str(kp))
    key = licence.load_key()
    code = licence.make_code(key, "DEV-123456", "ALL", 0, "a|b@x.com")
    assert licence.verify_code(key.public_key(), code)
    assert licence.unb64u(code.split(".")[1]) == b"DEV-123456|ALL|0|a b@x.com"

def test_latest_apk_redirect(c, tmp_path, monkeypatch):
    monkeypatch.setenv("FEED_DIR", str(tmp_path))
    assert c.get("/api/latest.apk", follow_redirects=False).status_code == 404
    (tmp_path / "version.json").write_text('{"apkUrl":"https://servmod.com/servmod/releases/ServMod-0.27.0.apk"}')
    r = c.get("/api/latest.apk", follow_redirects=False)
    assert r.status_code == 302 and r.headers["location"].endswith("ServMod-0.27.0.apk")
    (tmp_path / "version.json").write_text('{"apkUrl":"https://evil.example/x.apk"}')
    assert c.get("/api/latest.apk", follow_redirects=False).status_code == 404

def test_waitlist_double_optin_and_unsub(c):
    from servmod_api import mail, core
    assert c.post("/api/waitlist", json={"email": "bad"}, headers=H).status_code == 400
    assert c.post("/api/waitlist", json={"email": "w@x.com"}, headers=H).status_code == 200
    assert len(mail.OUTBOX) == 1
    tok = re.search(r"#confirm=(\S+)", mail.OUTBOX[-1][2]).group(1)
    assert core.q("SELECT confirmed FROM waitlist").fetchone()[0] == 0
    assert c.post("/api/waitlist/confirm", json={"token": "nope"}, headers=H).status_code == 400
    assert c.post("/api/waitlist/confirm", json={"token": tok}, headers=H).status_code == 200
    assert core.q("SELECT confirmed FROM waitlist").fetchone()[0] == 1
    assert c.post("/api/waitlist", json={"email": "w@x.com"}, headers=H).status_code == 200  # generic, nothing more sent
    assert len(mail.OUTBOX) == 1
    assert c.post("/api/waitlist", json={"email": "h@x.com", "website": "spam"}, headers=H).status_code == 200
    assert core.q("SELECT COUNT(*) FROM waitlist").fetchone()[0] == 1  # honeypot
    assert c.post("/api/waitlist/unsubscribe", json={"token": tok}, headers=H).status_code == 200
    assert core.q("SELECT COUNT(*) FROM waitlist").fetchone()[0] == 0

def test_waitlist_account_toggle_and_admin_notify(c, monkeypatch):
    from servmod_api import mail, core, app as appmod
    monkeypatch.setattr(appmod.time, "sleep", lambda s: None)
    tok, _ = login(c, "u@x.com")
    c.post("/api/auth/verify", json={"token": tok}, headers=H)
    assert c.get("/api/me").json()["waitlist"] is False
    assert c.post("/api/waitlist/me", json={"on": True}, headers=H).json()["on"] is True
    assert c.get("/api/me").json()["waitlist"] is True
    assert c.post("/api/admin/waitlist/notify", json={"subject": "s", "text": "long enough text", "confirm": True}, headers=H).status_code == 403
    c.post("/api/auth/logout", headers=H)
    tok, _ = login(c, "boss@x.com")
    c.post("/api/auth/verify", json={"token": tok}, headers=H)
    assert c.get("/api/admin/overview").json()["waitlist"]["confirmed"] == 1
    assert c.post("/api/admin/waitlist/notify", json={"subject": "Released", "text": "ServMod is out now"}, headers=H).status_code == 400  # needs confirm
    n = len(mail.OUTBOX)
    assert c.post("/api/admin/waitlist/notify", json={"subject": "Released", "text": "ServMod is out now", "test": True}, headers=H).json()["test"]
    assert mail.OUTBOX[-1][0] == "boss@x.com" and len(mail.OUTBOX) == n + 1
    r = c.post("/api/admin/waitlist/notify", json={"subject": "Released", "text": "ServMod is out now", "confirm": True}, headers=H).json()
    assert r["queued"] == 1
    import time; time.sleep(0.3)
    assert mail.OUTBOX[-1][0] == "u@x.com" and "Unsubscribe" in mail.OUTBOX[-1][2]
    assert core.q("SELECT notified FROM waitlist").fetchone()[0] is not None
    assert c.post("/api/admin/waitlist/notify", json={"subject": "Released", "text": "ServMod is out now", "confirm": True}, headers=H).json()["queued"] == 0


def _stripe_event(secret, obj, typ="checkout.session.completed", t=None):
    import hmac, hashlib, json, time
    raw = json.dumps({"type": typ, "data": {"object": obj}}).encode()
    t = int(t or time.time())
    sig = hmac.new(secret.encode(), f"{t}.".encode() + raw, hashlib.sha256).hexdigest()
    return raw, {"Stripe-Signature": f"t={t},v1={sig}", "Content-Type": "application/json"}

def test_shop_closed_by_default(c):
    assert c.get("/api/shop/config").json()["open"] is False
    assert c.post("/api/shop/checkout", json={"product": "pro"}, headers=H).status_code == 503

def test_stripe_webhook_grants_and_issues_code(c, monkeypatch):
    from servmod_api import licence, mail
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x"); monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_x")
    obj = {"id": "cs_1", "payment_status": "paid", "amount_total": 4000, "currency": "gbp", "metadata": {"product": "pro"},
           "customer_details": {"email": "Buyer@x.com"}, "custom_fields": [{"key": "device_id", "text": {"value": "abcdef123"}}]}
    raw, h = _stripe_event("whsec_x", obj)
    assert c.post("/api/pay/stripe", content=raw, headers=h).json()["result"] == "new"   # no CSRF header needed, signature instead
    code = re.search(r"(WL1\.\S+)", mail.OUTBOX[-1][2]).group(1)
    assert licence.verify_code(c.key.public_key(), code) and licence.code_features(code) == "PRO"
    assert c.post("/api/pay/stripe", content=raw, headers=h).json()["result"] == "duplicate"   # replayed event
    # subscription later extends and re-issues the code for the same device
    obj2 = dict(obj, id="cs_2", amount_total=2000, metadata={"product": "sub"}, custom_fields=[])
    raw2, h2 = _stripe_event("whsec_x", obj2)
    assert c.post("/api/pay/stripe", content=raw2, headers=h2).json()["result"] == "new"
    tok, _ = login(c, "buyer@x.com"); c.post("/api/auth/verify", json={"token": tok}, headers=H)
    new = c.post("/api/devices", json={"device_id": "ABCDEF123"}, headers=H).json()["code"]
    assert licence.code_features(new).startswith("PRO,SUB:") and licence.verify_code(c.key.public_key(), new)

def test_stripe_webhook_rejects_bad_signature_and_old_events(c, monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_x")
    obj = {"id": "cs_9", "payment_status": "paid", "metadata": {"product": "pro"}, "customer_details": {"email": "a@b.com"}}
    raw, h = _stripe_event("wrong", obj)
    assert c.post("/api/pay/stripe", content=raw, headers=h).status_code == 400
    raw, h = _stripe_event("whsec_x", obj, t=1000)
    assert c.post("/api/pay/stripe", content=raw, headers=h).status_code == 400
    raw, h = _stripe_event("whsec_x", dict(obj, payment_status="unpaid"))
    assert c.post("/api/pay/stripe", content=raw, headers=h).json()["ok"] is True
    assert c.get("/api/me").status_code == 401
