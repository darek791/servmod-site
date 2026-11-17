"""Static fault-code and parameter pages (indexable), built from manuals_src/data/*.json (our own summaries)."""
import os, re, json, glob, html

DRIVES = {
    "wj200": dict(name="Hitachi WJ200", maker="Hitachi", dev="hitachi-wj200", wiring="hitachi-wj200"),
    "fc280": dict(name="Danfoss VLT FC 280", maker="Danfoss", dev="danfoss-fc-280", wiring="danfoss-fc280"),
    "mx2": dict(name="Omron MX2", maker="Omron", dev="omron-mx2", wiring="omron-mx2"),
    "pf520": dict(name="Allen-Bradley PowerFlex 525", short="PowerFlex 525", maker="Allen-Bradley", dev="allen-bradley-powerflex-525", wiring="pf525"),
}
FAULT_LINK = {v["dev"]: f"/fault-codes/{k}/" for k, v in DRIVES.items()}
e = html.escape


def _slug(code, used):
    s = re.sub(r"[^a-z0-9]+", "-", str(code).lower()).strip("-") or "x"
    base, i = s, 2
    while s in used:
        s = f"{base}-{i}"; i += 1
    used.add(s)
    return s


def _cut(t, n):
    t = " ".join(t.split())
    if len(t) <= n:
        return t
    return t[:n].rsplit(" ", 1)[0].rstrip(",;:.") + "..."


def _crumbs(DOMAIN, items):
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + p} for i, (n, p) in enumerate(items)]}) + "</script>"


def make(page, DOMAIN, ICON_SVG, HERE):
    out = {}
    data = {}
    for f in sorted(glob.glob(os.path.join(HERE, "..", "manuals_src", "data", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        if d["id"] in DRIVES:
            data[d["id"]] = d
    disc = ("<p class=\"hint\">This is a short summary written by ServMod. It can contain mistakes or be out of date. Check the manufacturer's current manual "
            "before changing settings or opening a drive. ServMod is independent and is not made, approved or supported by the manufacturer. "
            "Work on live equipment only if you are qualified, and isolate and lock out the supply first.</p>")
    cta = (f'<p class="actions"><a class="btn" data-dl href="/download.html">{ICON_SVG} Download free for Android</a></p>')
    # top index
    cards = ""
    for k, dv in DRIVES.items():
        d = data[k]
        cards += (f'<li><a href="/fault-codes/{k}/"><strong>{e(dv["name"])}</strong></a>: {len(d["faults"])} fault and warning codes, '
                  f'<a href="/parameters/{k}/">{len(d["params"])} parameters</a></li>')
    body = f"""<div class="wrap page"><div class="prose" style="max-width:none">
<h1>Inverter fault codes and parameters</h1>
<p class="intro">Plain-English meaning and a checklist for the fault codes of the drives ServMod works with. Each answer points to the page of the manufacturer's manual it comes from.</p>
<ul>{cards}</ul>
<p>Prefer to search? <a href="/manuals/">Open the search tool</a>. The same fault codes, wiring diagrams and parameter lists are inside the free <a href="/download.html">ServMod app</a>, which works fully offline.</p>
{cta}{disc}</div></div>"""
    out["fault-codes/index.html"] = page("manuals", "Inverter fault codes and parameters",
        "Fault codes and parameters for Hitachi WJ200, Danfoss FC 280, Omron MX2 and Allen-Bradley PowerFlex 520: meaning, checks and the manual page.", body, "/fault-codes/",
        extra_head=_crumbs(DOMAIN, [("ServMod", "/"), ("Fault codes", "/fault-codes/")]))
    for k, dv in DRIVES.items():
        d = data[k]; used = set(); codes = []
        for fl in d["faults"]:
            codes.append((fl, _slug(fl["code"], used)))
        name = dv["name"]; doc = d["doc"]
        docline = f'{e(doc["name"])} ({e(doc["number"])}, {e(doc["date"])})'
        # hub
        rows = "".join(f'<tr><td><a href="/fault-codes/{k}/{s}.html"><strong>{e(str(fl["code"]))}</strong></a></td><td>{e(fl["name"])}</td><td>{e(_cut(fl["meaning"], 110))}</td></tr>' for fl, s in codes)
        body = f"""<div class="wrap page"><div class="prose" style="max-width:none">
<p class="hint"><a href="/fault-codes/">Fault codes</a> / {e(name)}</p>
<h1>{e(name)} fault codes: meaning and checks</h1>
<p class="intro">{len(codes)} fault and warning codes of the {e(name)}, each with what it means and what to check first. Tap a code for the full checklist.</p>
<div style="overflow-x:auto"><table class="plans"><thead><tr><th>Code</th><th>Name</th><th>Meaning</th></tr></thead><tbody>{rows}</tbody></table></div>
<p>Source: {docline}. <a href="{e(doc["url"])}" rel="noopener" target="_blank">Manufacturer page</a>. See also the <a href="/parameters/{k}/">{e(name)} parameter list</a>, the <a href="/equipment/{dv["dev"]}.html">connection and backup page</a> and the <a href="/wiring.html#{dv["wiring"]}">wiring diagrams</a>.</p>
{cta}{disc}</div></div>"""
        out[f"fault-codes/{k}/index.html"] = page("manuals", f"{name} fault codes: meaning and checks",
            f"All {len(codes)} fault codes of the {name} with meaning and a short checklist for each, plus the page of the manufacturer's manual.", body, f"/fault-codes/{k}/",
            extra_head=_crumbs(DOMAIN, [("ServMod", "/"), ("Fault codes", "/fault-codes/"), (name, f"/fault-codes/{k}/")]))
        chips = "".join(f'<a href="/fault-codes/{k}/{s}.html">{e(str(fl["code"]))}</a>' for fl, s in codes)
        for fl, s in codes:
            code = str(fl["code"]); path = f"/fault-codes/{k}/{s}.html"
            checks = "".join(f"<li>{e(c)}</li>" for c in fl.get("checks", []))
            kind = fl.get("kind")
            kindtxt = f" ({e(kind)})" if kind else ""
            pg = f", page {fl['page']}" if fl.get("page") else ""
            title = f"{dv.get('short', name)} {code}: {fl['name']}"
            desc = _cut(f"{name} {code} {fl['name']}. {fl['meaning']} Checks: " + "; ".join(fl.get("checks", [])[:3]), 158)
            body = f"""<div class="wrap page"><div class="prose" style="max-width:none">
<p class="hint"><a href="/fault-codes/">Fault codes</a> / <a href="/fault-codes/{k}/">{e(name)}</a> / {e(code)}</p>
<h1>{e(name)} fault {e(code)}: {e(fl["name"])}</h1>
<p class="intro">{e(fl["meaning"])}</p>
<h2>What to check</h2>
<ol>{checks}</ol>
<p>Source: {docline}{pg}{kindtxt}. <a href="{e(doc["url"])}" rel="noopener" target="_blank">Manufacturer page</a>.</p>
<h2>Keep the settings safe before you change anything</h2>
<p>Before you reset, replace or reprogram a {e(name)}, save all its parameters to your phone with ServMod, so a replacement can be set up in minutes. See how to <a href="/equipment/{dv["dev"]}.html">connect the {e(name)} to a phone</a> and the <a href="/wiring.html#{dv["wiring"]}">wiring diagrams</a>.</p>
{cta}
<h2>Other {e(name)} fault codes</h2>
<p class="chips">{chips}</p>
{disc}</div></div>"""
            out[f"fault-codes/{k}/{s}.html"] = page("manuals", title, desc, body, path,
                extra_head=_crumbs(DOMAIN, [("ServMod", "/"), ("Fault codes", "/fault-codes/"), (name, f"/fault-codes/{k}/"), (code, path)]))
        # parameters
        prow = "".join(f'<tr><td><strong>{e(str(p["id"]))}</strong></td><td>{e(p["name"])}</td><td>{e(str(p.get("range", "")))}</td><td>{e(str(p.get("default", "")))}</td><td>{e(p.get("desc", ""))}</td></tr>' for p in d["params"])
        body = f"""<div class="wrap page"><div class="prose" style="max-width:none">
<p class="hint"><a href="/fault-codes/">Fault codes</a> / {e(name)} parameters</p>
<h1>{e(name)} parameter list</h1>
<p class="intro">{len(d["params"])} parameters of the {e(name)} with range, default value and a short description. Source: {docline}.</p>
<div style="overflow-x:auto"><table class="plans"><thead><tr><th>No.</th><th>Name</th><th>Range</th><th>Default</th><th>What it does</th></tr></thead><tbody>{prow}</tbody></table></div>
<p>See also the <a href="/fault-codes/{k}/">{e(name)} fault codes</a>. ServMod reads, compares and backs up these parameters from your phone: <a href="/equipment/{dv["dev"]}.html">how to connect</a>.</p>
{cta}{disc}</div></div>"""
        out[f"parameters/{k}/index.html"] = page("manuals", f"{name} parameter list",
            f"{name} parameter list: {len(d['params'])} parameters with range, default and a short description, from the manufacturer's manual.", body, f"/parameters/{k}/",
            extra_head=_crumbs(DOMAIN, [("ServMod", "/"), ("Fault codes", "/fault-codes/"), (f"{name} parameters", f"/parameters/{k}/")]))
    return out
