"""Issue (or re-issue) an activation code for a user's device. Used by the account page and by the shop."""
from fastapi import HTTPException
from . import core, licence

def moves_used(ent_id):
    return core.q("SELECT COUNT(*) c FROM licences WHERE entitlement_id=? AND released>?", (ent_id, core.now() - 365 * 86400)).fetchone()["c"]

def issue(u, dev, label=""):
    ent_rows = core.q("SELECT * FROM entitlements WHERE user_id=? AND revoked=0 ORDER BY id", (u["id"],)).fetchall()
    if not ent_rows: raise HTTPException(402, "no licence on this account")
    for e in ent_rows:  # same device again -> same code, re-signed only when the plan changed
        ex = core.q("SELECT * FROM licences WHERE entitlement_id=? AND device_id=? AND released IS NULL", (e["id"], dev)).fetchone()
        if ex:
            if licence.code_features(ex["code"]) == e["features"]: return ex["code"]
            try: key = licence.load_key()
            except Exception: raise HTTPException(503, "licence signing is not configured yet")
            code = licence.make_code(key, dev, e["features"], 0, u["email"])
            core.q("UPDATE licences SET code=? WHERE id=?", (code, ex["id"]))
            core.audit(u["email"], "licence-reissue", dev)
            return code
    for e in ent_rows:
        active = core.q("SELECT COUNT(*) c FROM licences WHERE entitlement_id=? AND released IS NULL", (e["id"],)).fetchone()["c"]
        if active < e["seats"]:
            if core.q("SELECT 1 FROM licences WHERE entitlement_id=?", (e["id"],)).fetchone() and moves_used(e["id"]) >= core.MOVES_PER_YEAR:
                raise HTTPException(409, "device move limit reached; contact support")
            try: key = licence.load_key()
            except Exception: raise HTTPException(503, "licence signing is not configured yet")
            code = licence.make_code(key, dev, e["features"], 0, u["email"])
            core.q("INSERT INTO licences(entitlement_id,device_id,label,code,created) VALUES(?,?,?,?,?)", (e["id"], dev, label, code, core.now()))
            core.audit(u["email"], "licence", dev)
            return code
    raise HTTPException(409, "all seats are in use; release a device first")
