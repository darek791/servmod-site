#!/usr/bin/env python3
"""Publish a signed ServMod APK to the update feed on servmod.com.

  python release.py ServMod-0.27.0.apk --notes "Fixed X;Added Y" [--channel stable|beta]
        [--notes-file notes.txt] [--changelog-url URL] [--min-version-code N]
        [--sign-key feed_private.key] [--dry-run] [--host root@167.233.108.235] [--ssh-key PATH]

versionCode / versionName are read from the APK itself. sha256 and size are computed.
Refuses to publish a versionCode that is not higher than the newest already published
on that channel. Layout on the server (never touched by the site sync):
  /var/www/servmod/servmod/version.json, beta/version.json, history.json, releases/ServMod-<name>.apk
Keeps the last 10 APKs. Needs OpenSSH (ssh, scp) on this PC.
Optional feed signature: ECDSA P-256 (SHA-256) over canonical JSON of the feed without the
"signature" field (keys sorted, separators ",", ":", UTF-8); stored as base64url DER.
"""
import argparse, base64, datetime, hashlib, json, os, secrets, struct, subprocess, sys, tempfile, zipfile

DOMAIN = "https://servmod.com"
REMOTE = "/var/www/servmod/servmod"
KEEP = 10

# ---------- minimal Android binary XML reader (AndroidManifest.xml) ----------
def read_manifest(apk):
    data = zipfile.ZipFile(apk).read("AndroidManifest.xml")
    if struct.unpack_from("<H", data, 0)[0] != 3: raise SystemExit("AndroidManifest.xml is not binary XML")
    pos = struct.unpack_from("<H", data, 2)[0]
    strings, attrs = [], {}
    while pos + 8 <= len(data):
        ctype, hsize, size = struct.unpack_from("<HHI", data, pos)
        if ctype == 0x0001:  # string pool
            count = struct.unpack_from("<I", data, pos + 8)[0]
            flags = struct.unpack_from("<I", data, pos + 16)[0]
            sstart = struct.unpack_from("<I", data, pos + 20)[0]
            utf8 = bool(flags & 0x100)
            offs = struct.unpack_from("<%dI" % count, data, pos + hsize)
            base = pos + sstart
            for o in offs:
                p = base + o
                if utf8:
                    n = data[p]; p += 1 if n < 0x80 else 2
                    n = data[p]; p += 1
                    if n & 0x80: n = ((n & 0x7F) << 8) | data[p]; p += 1
                    strings.append(data[p:p + n].decode("utf-8", "replace"))
                else:
                    n = struct.unpack_from("<H", data, p)[0]; p += 2
                    if n & 0x8000: n = ((n & 0x7FFF) << 16) | struct.unpack_from("<H", data, p)[0]; p += 2
                    strings.append(data[p:p + n * 2].decode("utf-16le", "replace"))
        elif ctype == 0x0102:  # start element
            ns, name, astart, asize, acount = struct.unpack_from("<iiHHH", data, pos + 16)
            if strings[name] == "manifest":
                ap = pos + 16 + astart
                for i in range(acount):
                    _, an, raw, vsize, _, vtype, vdata = struct.unpack_from("<iiiHBBi", data, ap + i * asize)
                    attrs[strings[an]] = strings[raw] if raw >= 0 else vdata
                break
        pos += size
    try: return int(attrs["versionCode"]), str(attrs["versionName"]), str(attrs.get("package", ""))
    except KeyError: raise SystemExit("could not read versionCode/versionName from the APK")

# ---------- optional signature (pure Python P-256) ----------
P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
A = P - 3
N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
G = (0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296, 0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5)
def _add(p, q):
    if p is None: return q
    if q is None: return p
    if p[0] == q[0] and (p[1] + q[1]) % P == 0: return None
    m = (3 * p[0] * p[0] + A) * pow(2 * p[1], -1, P) % P if p == q else (q[1] - p[1]) * pow(q[0] - p[0], -1, P) % P
    x = (m * m - p[0] - q[0]) % P
    return (x, (m * (p[0] - x) - p[1]) % P)
def _mul(k, p):
    r = None
    while k:
        if k & 1: r = _add(r, p)
        p = _add(p, p); k >>= 1
    return r
def _der(v):
    b = v.to_bytes((v.bit_length() + 8) // 8, "big"); return b"\x02" + bytes([len(b)]) + b
def sign(priv, msg):
    z = int.from_bytes(hashlib.sha256(msg).digest(), "big")
    while True:
        k = secrets.randbelow(N - 1) + 1
        r = _mul(k, G)[0] % N
        if not r: continue
        s = pow(k, -1, N) * (z + r * priv) % N
        if s: break
    body = _der(r) + _der(s); return b"\x30" + bytes([len(body)]) + body
def b64u(b): return base64.urlsafe_b64encode(b).rstrip(b"=").decode()
def canonical(d):
    return json.dumps({k: v for k, v in d.items() if k != "signature"}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

# ---------- ssh helpers ----------
def ssh_args(a): return ["-i", a.ssh_key] if a.ssh_key else []
def run_ssh(a, cmd, inp=None):
    return subprocess.run(["ssh"] + ssh_args(a) + [a.host, cmd], input=inp, capture_output=True, text=True)
def fetch(a, path):
    r = run_ssh(a, f"cat {REMOTE}/{path} 2>/dev/null")
    try: return json.loads(r.stdout) if r.stdout.strip() else None
    except ValueError: return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("apk"); ap.add_argument("--notes", default=""); ap.add_argument("--notes-file")
    ap.add_argument("--channel", choices=["stable", "beta"], default="stable")
    ap.add_argument("--changelog-url"); ap.add_argument("--min-version-code", type=int, default=0)
    ap.add_argument("--sign-key"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--host", default="root@167.233.108.235")
    ap.add_argument("--ssh-key", default=os.path.join(os.path.expanduser("~"), ".ssh", "id_ed25519"))
    a = ap.parse_args()
    if not os.path.isfile(a.apk): sys.exit("APK not found: " + a.apk)
    code, name, pkg = read_manifest(a.apk)
    if not name.replace(".", "").replace("-", "").replace("_", "").isalnum(): sys.exit("odd versionName: " + name)
    notes = [n.strip() for n in (open(a.notes_file, encoding="utf-8").read().splitlines() if a.notes_file else a.notes.split(";")) if n.strip()]
    if not notes: sys.exit("give release notes (--notes 'a;b' or --notes-file)")
    sha = hashlib.sha256(open(a.apk, "rb").read()).hexdigest(); size = os.path.getsize(a.apk)
    feed_path = "version.json" if a.channel == "stable" else "beta/version.json"
    cur = fetch(a, feed_path); hist = fetch(a, "history.json") or []
    top = max([h["versionCode"] for h in hist if h.get("channel", "stable") == a.channel] + ([cur["versionCode"]] if cur else [0]))
    print(f"package {pkg}  versionName {name}  versionCode {code}  size {size}  sha256 {sha[:16]}…  channel {a.channel}")
    print(f"newest published on {a.channel}: {top or 'none'}")
    if code <= top: sys.exit(f"REFUSED: versionCode {code} is not higher than {top}")
    today = datetime.date.today().isoformat()
    fname = f"ServMod-{name}.apk"
    feed = {"versionCode": code, "versionName": name, "channel": a.channel, "apkUrl": f"{DOMAIN}/servmod/releases/{fname}",
            "sha256": sha, "size": size, "minVersionCode": a.min_version_code, "date": today, "notes": notes}
    if a.changelog_url: feed["changelogUrl"] = a.changelog_url
    if a.sign_key:
        priv = int(open(a.sign_key).read().strip(), 16)
        feed["signature"] = b64u(sign(priv, canonical(feed)))
    hist = [h for h in hist if h.get("versionCode") != code] + [{"versionCode": code, "versionName": name, "channel": a.channel, "date": today, "notes": notes, "size": size, "sha256": sha}]
    hist.sort(key=lambda h: h["versionCode"], reverse=True)
    if a.dry_run:
        print(json.dumps(feed, indent=2)); print("dry run: nothing uploaded"); return
    tmp = tempfile.mkdtemp()
    open(os.path.join(tmp, "feed.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(feed, indent=2, ensure_ascii=False) + "\n")
    open(os.path.join(tmp, "history.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(hist, indent=2, ensure_ascii=False) + "\n")
    stage = f"/tmp/servmod-rel-{code}"
    r = run_ssh(a, f"rm -rf {stage} && mkdir -p {stage}")
    for src, dst in ((a.apk, fname), (os.path.join(tmp, "feed.json"), "feed.json"), (os.path.join(tmp, "history.json"), "history.json")):
        r = subprocess.run(["scp"] + ssh_args(a) + [src, f"{a.host}:{stage}/{dst}"])
        if r.returncode: sys.exit("upload failed")
    remote = f"""set -e
R={REMOTE}; mkdir -p $R/releases $R/beta
echo "{sha}  {stage}/{fname}" | sha256sum -c - >/dev/null
install -m 644 {stage}/{fname} $R/releases/{fname}
install -m 644 {stage}/history.json $R/history.json.new && mv $R/history.json.new $R/history.json
install -m 644 {stage}/feed.json $R/{feed_path}.new && mv $R/{feed_path}.new $R/{feed_path}
chown -R www-data:www-data $R
ls -1t $R/releases/*.apk | tail -n +{KEEP + 1} | xargs -r rm -f
rm -rf {stage}
echo published
"""
    r = run_ssh(a, "bash -s", inp=remote.replace("\r", ""))
    print(r.stdout.strip(), r.stderr.strip())
    if "published" not in r.stdout: sys.exit("publish step failed")
    print(f"OK. Feed: {DOMAIN}/servmod/{feed_path}\n    APK:  {feed['apkUrl']}")

if __name__ == "__main__": main()
