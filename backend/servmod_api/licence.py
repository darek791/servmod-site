"""Activation codes WL1.<b64url(payload)>.<b64url(DER ecdsa-sha256 sig)>; payload DEVICE|FEATURES|EXP|NAME."""
import base64, os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

KEY_PATH = lambda: os.environ.get("LICENSE_KEY", "/etc/servmod/license_private.key")

def b64u(b: bytes) -> str: return base64.urlsafe_b64encode(b).decode().rstrip("=")
def unb64u(s: str) -> bytes: return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

def load_key():
    """Accepts the 64-hex-digit private scalar written by wl200_license.py keygen, or a PEM file."""
    with open(KEY_PATH(), "rb") as f: raw = f.read().strip()
    if len(raw) == 64 and all(c in b"0123456789abcdefABCDEF" for c in raw):
        return ec.derive_private_key(int(raw, 16), ec.SECP256R1())
    return serialization.load_pem_private_key(raw, None)

def make_code(key, device, features, exp=0, name=""):
    payload = "|".join([device, features, str(exp), name.replace("|", " ")]).encode()
    sig = key.sign(payload, ec.ECDSA(hashes.SHA256()))
    return f"WL1.{b64u(payload)}.{b64u(sig)}"

def verify_code(pub, code):
    try:
        tag, p, s = code.split(".")
        pub.verify(unb64u(s), unb64u(p), ec.ECDSA(hashes.SHA256()))
        return tag == "WL1"
    except Exception:
        return False

def code_features(code: str) -> str:
    """FEATURES field of a code's payload ('' when the code cannot be parsed)."""
    try: return unb64u(code.split(".")[1]).decode().split("|")[1]
    except Exception: return ""
