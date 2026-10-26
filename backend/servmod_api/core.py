"""Config, SQLite, hashing, sessions, rate limiting."""
import hashlib, hmac, os, secrets, sqlite3, time, threading, re

def _load_env_file(path):
    """Secrets typed on the PC land in /etc/servmod/pay.env (not in the repo). Real environment variables win."""
    try:
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())
    except OSError:
        pass
_load_env_file(os.environ.get("PAY_ENV", "/etc/servmod/pay.env"))

DATA_DIR = os.environ.get("SERVMOD_DATA", "/var/lib/servmod")
SITE_URL = os.environ.get("SITE_URL", "https://servmod.com")
ADMIN_EMAILS = {e.strip().lower() for e in os.environ.get("ADMIN_EMAILS", "").split(",") if e.strip()}
SESSION_DAYS = 30
TOKEN_TTL = 15 * 60
MAX_CODE_TRIES = 5
MOVES_PER_YEAR = 3
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,255}\.[^@\s.]{2,}$")
DEVICE_RE = re.compile(r"^[A-Z0-9][A-Z0-9-]{5,63}$")

_lock = threading.Lock()
_conn = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, created INTEGER NOT NULL, last_login INTEGER);
CREATE TABLE IF NOT EXISTS login_tokens(id INTEGER PRIMARY KEY, email TEXT NOT NULL, link_hash TEXT NOT NULL, code_hash TEXT NOT NULL, expires INTEGER NOT NULL, tries INTEGER NOT NULL DEFAULT 0, used INTEGER NOT NULL DEFAULT 0);
CREATE INDEX IF NOT EXISTS ix_lt_link ON login_tokens(link_hash);
CREATE TABLE IF NOT EXISTS sessions(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, tok_hash TEXT UNIQUE NOT NULL, expires INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS entitlements(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, product TEXT NOT NULL, features TEXT NOT NULL, seats INTEGER NOT NULL DEFAULT 1, source TEXT NOT NULL, created INTEGER NOT NULL, revoked INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS licences(id INTEGER PRIMARY KEY, entitlement_id INTEGER NOT NULL, device_id TEXT NOT NULL, label TEXT, code TEXT NOT NULL, created INTEGER NOT NULL, released INTEGER);
CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY, created INTEGER NOT NULL, user_id INTEGER, email TEXT NOT NULL, subject TEXT, message TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open');
CREATE TABLE IF NOT EXISTS requests(id INTEGER PRIMARY KEY, created INTEGER NOT NULL, email TEXT, kind TEXT NOT NULL, device TEXT NOT NULL, protocol TEXT, connection TEXT, details TEXT, status TEXT NOT NULL DEFAULT 'new');
CREATE TABLE IF NOT EXISTS waitlist(id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, created INTEGER NOT NULL, confirmed INTEGER NOT NULL DEFAULT 0, tok TEXT UNIQUE NOT NULL, source TEXT, notified INTEGER);
CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, provider TEXT NOT NULL, ext_id TEXT NOT NULL, email TEXT NOT NULL, product TEXT NOT NULL, pence INTEGER NOT NULL, currency TEXT NOT NULL, created INTEGER NOT NULL, device_id TEXT, note TEXT, UNIQUE(provider, ext_id));
CREATE TABLE IF NOT EXISTS pending_orders(ext_id TEXT PRIMARY KEY, provider TEXT NOT NULL, product TEXT NOT NULL, device_id TEXT, claim TEXT, created INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS rate(k TEXT NOT NULL, ts INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS ix_rate ON rate(k, ts);
CREATE TABLE IF NOT EXISTS audit(ts INTEGER NOT NULL, actor TEXT, action TEXT, detail TEXT);
"""

def db():
    global _conn
    if _conn is None:
        os.makedirs(DATA_DIR, exist_ok=True)
        _conn = sqlite3.connect(os.path.join(DATA_DIR, "servmod.db"), check_same_thread=False, isolation_level=None)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("PRAGMA foreign_keys=ON")
        _conn.executescript(SCHEMA)
    return _conn

def reset(data_dir=None):
    global _conn, DATA_DIR
    if _conn: _conn.close()
    _conn = None
    if data_dir: DATA_DIR = data_dir

def q(sql, args=()):
    with _lock:
        return db().execute(sql, args)

def now(): return int(time.time())

def h(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def norm_email(e: str):
    e = (e or "").strip().lower()
    return e if EMAIL_RE.match(e) and len(e) <= 254 else None

def audit(actor, action, detail=""):
    q("INSERT INTO audit VALUES(?,?,?,?)", (now(), actor, action, detail[:500]))

def rate_ok(key: str, limit: int, window: int) -> bool:
    t = now()
    q("DELETE FROM rate WHERE ts<?", (t - 86400,))
    n = q("SELECT COUNT(*) c FROM rate WHERE k=? AND ts>?", (key, t - window)).fetchone()["c"]
    if n >= limit: return False
    q("INSERT INTO rate VALUES(?,?)", (key, t))
    return True

# ---- login tokens
def create_login(email):
    link = secrets.token_urlsafe(32)
    code = f"{secrets.randbelow(10**6):06d}"
    q("UPDATE login_tokens SET used=1 WHERE email=? AND used=0", (email,))
    q("INSERT INTO login_tokens(email,link_hash,code_hash,expires) VALUES(?,?,?,?)",
      (email, h(link), h(email + ":" + code), now() + TOKEN_TTL))
    return link, code

def _user_for(email):
    q("INSERT OR IGNORE INTO users(email,created) VALUES(?,?)", (email, now()))
    return q("SELECT * FROM users WHERE email=?", (email,)).fetchone()

def consume_link(link):
    r = q("SELECT * FROM login_tokens WHERE link_hash=? AND used=0 AND expires>?", (h(link), now())).fetchone()
    if not r: return None
    q("UPDATE login_tokens SET used=1 WHERE id=?", (r["id"],))
    return _user_for(r["email"])

def consume_code(email, code):
    r = q("SELECT * FROM login_tokens WHERE email=? AND used=0 AND expires>? ORDER BY id DESC LIMIT 1", (email, now())).fetchone()
    if not r: return None
    if r["tries"] >= MAX_CODE_TRIES:
        q("UPDATE login_tokens SET used=1 WHERE id=?", (r["id"],)); return None
    q("UPDATE login_tokens SET tries=tries+1 WHERE id=?", (r["id"],))
    if not hmac.compare_digest(r["code_hash"], h(email + ":" + (code or "").strip())): return None
    q("UPDATE login_tokens SET used=1 WHERE id=?", (r["id"],))
    return _user_for(email)

def new_session(user_id):
    tok = secrets.token_urlsafe(32)
    q("INSERT INTO sessions(user_id,tok_hash,expires) VALUES(?,?,?)", (user_id, h(tok), now() + SESSION_DAYS * 86400))
    q("UPDATE users SET last_login=? WHERE id=?", (now(), user_id))
    q("DELETE FROM sessions WHERE expires<?", (now(),))
    return tok

def session_user(tok):
    if not tok: return None
    return q("SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.tok_hash=? AND s.expires>?", (h(tok), now())).fetchone()

def end_session(tok):
    q("DELETE FROM sessions WHERE tok_hash=?", (h(tok or ""),))
