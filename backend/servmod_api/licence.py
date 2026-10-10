"""Activation codes WL1.<b64url(payload)>.<b64url(DER ecdsa-sha256 sig)>; payload DEVICE|FEATURES|EXP|NAME."""
import base64, os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

KEY_PATH = lambda: os.environ.get("LICENSE_KEY", "/etc/servmod/license_private.key")

def b64u(b: bytes) -> str: return base64.urlsafe_b64encode(b).decode().rstrip("=")
def unb64u(s: str) -> bytes: return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

def load_key():
    with open(KEY_PATH(), "rb") as f: raw = f.read()
    try: return serialization.load_pem_private_key(raw, None)
    except ValueError:
        return serialization.load_der_private_key(unb64u(raw.decode().strip()) if raw[:1] != b"\x30" else raw, None)

def make_code(key, device, features, exp=0, name=""):
    payload = f"{device}|{features}|{exp}|{name}".encode()
    sig = key.sign(payload, ec.ECDSA(hashes.SHA256()))
    return f"WL1.{b64u(payload)}.{b64u(sig)}"

def verify_code(pub, code):
    try:
        tag, p, s = code.split(".")
        pub.verify(unb64u(s), unb64u(p), ec.ECDSA(hashes.SHA256()))
        return tag == "WL1"
    except Exception:
        return False
