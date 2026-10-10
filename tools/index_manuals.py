#!/usr/bin/env python3
"""Build the searchable manuals index.
Put PDFs + catalog.json in manuals_src/, run:  python tools/index_manuals.py
Writes site/manuals/index.json (per-page text) and copies PDFs to site/manuals/pdf/.
Only PDFs you have the right to redistribute should be copied; set "link" instead of "file"
in catalog.json to point to the maker's own download and index text from a local copy with "src"."""
import json, os, re, shutil, sys
from pypdf import PdfReader
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, OUT = os.path.join(ROOT, "manuals_src"), os.path.join(ROOT, "site", "manuals")
cat = json.load(open(os.path.join(SRC, "catalog.json"), encoding="utf-8"))["manuals"]
os.makedirs(os.path.join(OUT, "pdf"), exist_ok=True)
res = []
for m in cat:
    p = os.path.join(SRC, m.get("src") or m["file"])
    if not os.path.exists(p):
        print("skip (missing):", p); continue
    pages = []
    for t in (pg.extract_text() or "" for pg in PdfReader(p).pages):
        pages.append(re.sub(r"\s+", " ", t).strip())
    e = {k: m[k] for k in ("id", "title", "maker", "models", "lang") if k in m}
    if m.get("link"): e["url"] = m["link"]
    else:
        shutil.copy(p, os.path.join(OUT, "pdf", m["file"])); e["url"] = "/manuals/pdf/" + m["file"]
    e["pages"] = pages
    res.append(e); print("indexed", m["id"], len(pages), "pages")
json.dump({"manuals": res}, open(os.path.join(OUT, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
