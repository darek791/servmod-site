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
