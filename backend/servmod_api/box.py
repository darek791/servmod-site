"""ServMod Box firmware and wiring drawings: Pro only, checked on the server.

Files live outside the public web root (BOX_DIR, default /var/lib/servmod/box):
  firmware.json            manifest from the BOX project (version, per-file sha256/bytes/offset)
  firmware/<file>.bin      images
  schematics/<file>        wiring drawings (png/svg)
Who counts as Pro: a signed-in account with a non-revoked entitlement whose features contain PRO or ALL,
or the app presenting an active licence code of such an entitlement in the X-Licence header.
"""
import json, os, re
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from . import core, licence

router = APIRouter()
SAFE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
TYPES = {".bin": "application/octet-stream", ".png": "image/png", ".svg": "image/svg+xml"}

def box_dir(): return os.environ.get("BOX_DIR", "/var/lib/servmod/box")

def _is_pro(features: str) -> bool:
    parts = {p.strip() for p in (features or "").split(",")}
    return "PRO" in parts or "ALL" in parts

def pro_who(req: Request) -> str:
    """Return a label for the caller (e-mail or licence id) or raise 401/403."""
    code = (req.headers.get("x-licence") or "").strip()
    if code:
        if not core.rate_ok("boxlic:" + core.h(code)[:16], 60, 3600): raise HTTPException(429, "too many requests")
        try: pub = licence.load_key().public_key()
        except Exception: raise HTTPException(503, "licence checking is not configured yet")
        if not licence.verify_code(pub, code): raise HTTPException(401, "invalid licence code")
        r = core.q("""SELECT l.id,e.features,e.revoked FROM licences l JOIN entitlements e ON e.id=l.entitlement_id
                      WHERE l.code=? AND l.released IS NULL""", (code,)).fetchone()
        if not r or r["revoked"]: raise HTTPException(401, "licence is not active")
        if not _is_pro(r["features"]): raise HTTPException(403, "ServMod Pro is required")
        return f"licence:{r['id']}"
    u = core.session_user(req.cookies.get("sm_session"))
    if not u: raise HTTPException(401, "not signed in")
    for e in core.q("SELECT features FROM entitlements WHERE user_id=? AND revoked=0", (u["id"],)).fetchall():
        if _is_pro(e["features"]): return u["email"]
    raise HTTPException(403, "ServMod Pro is required")

def manifest():
    try:
        with open(os.path.join(box_dir(), "firmware.json"), encoding="utf-8") as f: return json.load(f)
    except Exception:
        raise HTTPException(404, "no firmware published yet")

def _serve(sub: str, name: str, allowed: set, who: str, kind: str):
    if not SAFE.match(name) or name not in allowed: raise HTTPException(404, "not found")
    path = os.path.join(box_dir(), sub, name)
    if not os.path.isfile(path): raise HTTPException(404, "not found")
    core.audit(who, kind, name)
    ext = os.path.splitext(name)[1].lower()
    headers = {"Content-Disposition": f'attachment; filename="{name}"'} if ext == ".bin" else {}
    return FileResponse(path, media_type=TYPES.get(ext, "application/octet-stream"), headers=headers)

@router.get("/api/box/firmware")
def firmware_manifest(req: Request):
    pro_who(req)
    m = manifest()
    for b in m.get("boxes", {}).values():
        for f in b.get("files", []): f["url"] = "/api/box/firmware/" + f["file"]
    m["schematics"] = [{"file": n, "url": "/api/box/doc/" + n} for n in sorted(_names("schematics"))]
    return m

def _names(sub):
    try: return {n for n in os.listdir(os.path.join(box_dir(), sub)) if SAFE.match(n) and os.path.splitext(n)[1].lower() in TYPES}
    except OSError: return set()

@router.get("/api/box/firmware/{name}")
def firmware_file(name: str, req: Request):
    who = pro_who(req)
    m = manifest()
    allowed = {f["file"] for b in m.get("boxes", {}).values() for f in b.get("files", [])}
    return _serve("firmware", name, allowed, who, "box-fw")

@router.get("/api/box/doc/{name}")
def schematic_file(name: str, req: Request):
    who = pro_who(req)
    return _serve("schematics", name, _names("schematics"), who, "box-doc")
