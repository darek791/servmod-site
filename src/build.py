#!/usr/bin/env python3
"""Builds the ServMod static site: python build.py  ->  ../site (or OUT env)."""
import os, shutil, datetime, html
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT", os.path.join(HERE, "..", "site"))
DOMAIN = "https://servmod.com"
APP_VERSION = "0.26"
TODAY = datetime.date.today().isoformat()

NAV = [("features", "/features.html", "Modules"), ("equipment", "/equipment.html", "Equipment"),
       ("guides", "/guides.html", "Connection guides"), ("manuals", "/manuals/", "Manuals"), ("pricing", "/pricing.html", "Pricing"),
       ("support", "/support.html", "Support")]

def page(key, title, desc, body, path, extra_head="", noindex=False):
    nav = "".join(f'<a href="{h}"{" aria-current=page" if k == key else ""}>{t}</a>' for k, h, t in NAV)
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    full_title = title if title.startswith("ServMod") else f"{title} - ServMod"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="theme-color" content="#000000">
<link rel="canonical" href="{DOMAIN}{path}">
<link rel="icon" href="/assets/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/assets/icon-180.png">
<meta property="og:type" content="website"><meta property="og:site_name" content="ServMod">
<meta property="og:title" content="{html.escape(full_title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{DOMAIN}{path}"><meta property="og:image" content="{DOMAIN}/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
{robots}
<link rel="preload" href="/fonts/saira-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/ibm-plex-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/style.css">{extra_head}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
  <a class="brand" href="/" aria-label="ServMod home"><img src="/assets/logo-wide.png" srcset="/assets/logo-wide.png 1x,/assets/logo-wide@2x.png 2x" width="172" height="30" alt="ServMod"></a>
  <button class="menu" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
  <nav class="nav" id="nav" aria-label="Main">{nav}<a class="btn" href="/pricing.html">Get ServMod</a></nav>
</div></header>
<main id="main">
{body}
</main>
{FOOTER}
<script src="/site.js" defer></script>
</body>
</html>
"""

FOOTER = f"""<footer><div class="wrap">
  <div class="block">
    <div><img src="/assets/logo-wide.png" width="196" height="34" alt="ServMod"><p>Service toolbox for Android, made for maintenance engineers.</p></div>
    <div><h4>Product</h4><ul><li><a href="/features.html">Modules</a></li><li><a href="/equipment.html">Supported equipment</a></li><li><a href="/guides.html">Connection guides</a></li><li><a href="/pricing.html">Pricing</a></li></ul></div>
    <div><h4>Help</h4><ul><li><a href="/support.html">Support</a></li><li><a href="/support.html#faq">FAQ</a></li></ul></div>
    <div><h4>Legal</h4><ul><li><a href="/terms.html">Terms of use</a></li><li><a href="/privacy.html">Privacy</a></li><li><a href="/refunds.html">Refunds</a></li><li><a href="/licence.html">Licence</a></li></ul></div>
  </div>
  <p class="fine">ServMod is an independent tool. It is not made, approved or supported by Hitachi, Omron, Rockwell Automation, Allen-Bradley, Honeywell or any other manufacturer. Product and company names belong to their owners. Use it at your own risk and bench-test before working on production equipment; it is not a safety function and not an emergency stop. App release {APP_VERSION}, in testing. Created by Dariusz Grabowski, United Kingdom.</p>
</div></footer>"""

HERO_SVG = """<svg viewBox="0 40 600 390" role="img" aria-label="Diagram: an Android phone connects through a USB to RS-485 adapter to the RS+ and RS- terminals of an inverter">
<g fill="none" stroke="#111" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">
  <text x="24" y="62" fill="#111" stroke="none" font-family="IBM Plex Mono,monospace" font-size="16" font-weight="500">Phone</text>
  <rect x="24" y="76" width="118" height="250" rx="16" fill="#fff"/>
  <rect x="36" y="100" width="94" height="204" rx="4"/>
  <path d="M60 88h46"/>
  <rect x="44" y="118" width="78" height="22" rx="2" fill="#111"/>
  <rect x="44" y="150" width="78" height="22" rx="2"/><rect x="44" y="182" width="78" height="22" rx="2" stroke="#b86400" stroke-width="3"/><rect x="44" y="214" width="78" height="22" rx="2"/><rect x="44" y="246" width="78" height="22" rx="2"/>
  <path d="M83 326V372H172"/>
  <rect x="172" y="346" width="110" height="52" rx="3" fill="#fff"/>
  <text x="227" y="378" text-anchor="middle" fill="#111" stroke="none" font-family="IBM Plex Mono,monospace" font-size="14.5" font-weight="500">USB-RS485</text>
  <text x="400" y="62" fill="#111" stroke="none" font-family="IBM Plex Mono,monospace" font-size="16" font-weight="500">Inverter</text>
  <rect x="400" y="76" width="176" height="276" rx="4" fill="#fff"/>
  <rect x="420" y="98" width="136" height="54" rx="2" fill="#111"/>
  <text x="488" y="136" text-anchor="middle" fill="#f28a00" stroke="none" font-family="IBM Plex Mono,monospace" font-size="30" font-weight="500">50.00</text>
  <circle cx="440" cy="188" r="9"/><circle cx="476" cy="188" r="9"/><circle cx="512" cy="188" r="9"/><circle cx="548" cy="188" r="9" stroke-opacity="0"/>
  <path d="M420 222h136M420 238h136M420 254h136" stroke-opacity=".35"/>
  <rect x="412" y="300" width="152" height="34" rx="2"/>
  <rect x="428" y="312" width="12" height="12" fill="#111"/><rect x="468" y="312" width="12" height="12" fill="#111"/><rect x="508" y="312" width="12" height="12" stroke-opacity=".35"/><rect x="540" y="312" width="12" height="12" stroke-opacity=".35"/>
  <text x="434" y="296" text-anchor="middle" fill="#111" stroke="none" font-family="IBM Plex Mono,monospace" font-size="16" font-weight="500">RS+</text>
  <text x="474" y="296" text-anchor="middle" fill="#111" stroke="none" font-family="IBM Plex Mono,monospace" font-size="16" font-weight="500">RS-</text>
</g>
<path d="M282 362H434V336" fill="none" stroke="#f28a00" stroke-width="3.5" class="flow" stroke-linejoin="round"/>
<path d="M282 382H474V336" fill="none" stroke="#111" stroke-width="3.5" class="flow slow" stroke-linejoin="round"/>
<g font-family="IBM Plex Mono,monospace" font-size="16" fill="#111"><text x="298" y="350" fill="#b86400" font-weight="500">A (D+)</text><text x="298" y="408" font-weight="500">B (D-)</text></g>
</svg>"""

def hero():
    return f"""<section class="hero"><div class="wrap">
  <div>
    <h1>Back up the drive before you touch it.</h1>
    <p class="lead">ServMod reads, saves and compares inverter parameters from your Android phone, over a USB-RS485 adapter. No laptop, no mobile signal, no software to install on a PC.</p>
    <div class="actions"><a class="btn" href="/pricing.html">Get ServMod</a><a class="btn ghost" href="#job">See how a job goes</a></div>
    <ul class="facts"><li>Works fully offline</li><li>Android 7.0 or newer</li><li>Hitachi, Allen-Bradley, Omron</li></ul>
  </div>
  <figure class="sheet" style="margin:0">{HERO_SVG}<figcaption><span>Fig. 1 Phone to drive over RS-485</span><span>Omron MX2 shown</span></figcaption></figure>
</div></section>"""

def strip():
    items = [("Hitachi", "WJ200, WL200"), ("Allen-Bradley", "PowerFlex 520, 525"), ("Omron", "3G3MX2 drives"),
             ("PLC, read only", "Omron FINS, Logix"), ("Label printers", "Honeywell PM45")]
    return '<div class="strip"><div class="wrap">' + "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in items) + "</div></div>"

JOB = """<section id="job"><div class="wrap split">
  <div>
    <h2>A job, from the cable to the checked write</h2>
    <p class="intro">The screens are the same for every supported drive, so you learn the routine once.</p>
    <ol class="steps">
      <li><h3>Connect</h3><p>Plug the USB-RS485 adapter into the phone and wire A and B to the drive. ServMod finds the adapter and asks for permission once.</p></li>
      <li><h3>Back up</h3><p>Read every parameter and save the backup on the phone. You can share it as a file or keep it as the reference for the machine.</p></li>
      <li><h3>Compare</h3><p>Set any backup against the drive, or the drive against factory settings, and see only what differs.</p></li>
      <li><h3>Write and check</h3><p>Change a value, write it, and read the drive again before you leave the machine.</p></li>
    </ol>
  </div>
  <div class="panel scroll">
    <div class="cap">Example: backup against the drive, differences only</div>
    <table class="tbl diff"><thead><tr><th>Code</th><th>Parameter</th><th class="r">Backup</th><th class="r">Drive</th></tr></thead>
    <tbody>
    <tr><td><code>F002</code></td><td>Acceleration time 1</td><td class="r">10.00 s</td><td class="r chg">15.00 s</td></tr>
    <tr><td><code>F003</code></td><td>Deceleration time 1</td><td class="r">10.00 s</td><td class="r chg">20.00 s</td></tr>
    <tr><td><code>b083</code></td><td>Carrier frequency</td><td class="r">5.0 kHz</td><td class="r chg">8.0 kHz</td></tr>
    </tbody></table>
  </div>
</div></section>"""

MODULES = [
 ("Inverters", "Hitachi WJ200 and WL200, Allen-Bradley PowerFlex 520 and 525, Omron 3G3MX2. Read, back up, restore, compare, edit, run the motor manually, and look up fault causes.", "test", "In field testing"),
 ("Printers", "Check the Ethernet port and test printing on Honeywell PM45 label printers. Keep your own printer list. Fault guide for the PM45 included.", "test", "In field testing"),
 ("PLC", "Read Omron (FINS over UDP) and Allen-Bradley (EtherNet/IP) controllers with live values and a change list. It never writes to the PLC.", "draft", "Draft, bench only"),
 ("Condition", "Vibration and condition checks using the phone's own sensors.", "test", "In field testing"),
 ("Network", "Network checks for the shop floor.", "test", "In field testing"),
 ("Calc", "Power, cable size (recommended and minimum), resistor colour code, wiring colours (UK) and Ethernet T568A/B.", "ready", "Ready"),
 ("Access", "Machine passwords in an encrypted vault, unlocked with the phone's screen lock.", "ready", "Ready"),
 ("Notes", "Service notes with photos and drawing on top of the photo.", "ready", "Ready"),
 ("Parts", "Search the warehouse list on the phone. Import CSV or XLSX files with automatic column matching.", "ready", "Ready"),
 ("ESP32 Loader", "Flash ESP32, ESP32-S3 and CYD boards over USB from .bin files, with checksum verification.", "ready", "Ready"),
 ("Steppers", "Test panel and fault guide for stepper drives.", "plan", "Planned"),
]
def status_legend():
    return '<div class="legend"><span class="st">Ready</span><span class="st test">In field testing</span><span class="st draft">Draft</span><span class="st plan">Planned</span></div>'
def module_rows(n=None):
    rows = MODULES if n is None else MODULES[:n]
    return "".join(f'<tr><td><b>{a}</b></td><td>{b}</td><td><span class="st {c}">{d}</span></td></tr>' for a, b, c, d in rows)

def home():
    body = hero() + strip() + JOB + f"""
<section><div class="wrap">
  <h2>One app, eleven tools</h2>
  <p class="intro">Inverters and printers come first. The rest are small tools that live in the same app, so one phone covers the service bag.</p>
  <div style="margin-top:32px" class="scroll">{status_legend()}
  <table class="tbl mods"><thead><tr><th>Module</th><th>What it does</th><th>Status</th></tr></thead><tbody>{module_rows()}</tbody></table></div>
  <p class="intro" style="margin-top:22px"><a href="/features.html">Module details</a></p>
</div></section>

<section><div class="wrap">
  <h2>Careful by design</h2>
  <div class="rules">
    <div><h3>Nothing leaves the phone</h3><p>Backups, printer lists, notes and passwords stay on the device. The only network request the app makes by itself is the check for a new version.</p></div>
    <div><h3>The PLC module only reads</h3><p>It has no write function at all, so you can look at a running controller without risking a change.</p></div>
    <div><h3>Passwords stay encrypted</h3><p>The Access vault uses AES-GCM through the Android keystore, hides itself from screenshots, and clears the clipboard after 30 seconds.</p></div>
    <div><h3>Manual names, not nicknames</h3><p>Parameters keep the codes and names from the manufacturer's manual, so what you read on screen matches the paper.</p></div>
  </div>
</div></section>

<section><div class="wrap split">
  <div>
    <h2>Made on the shop floor</h2>
    <p class="intro">ServMod is built by one maintenance engineer, Dariusz Grabowski, after 30 years across injection moulding, petrochemicals, refineries, robotics and car systems. Every module exists because a job needed it.</p>
  </div>
  <div class="stack">
    <p style="margin:0;color:#d4d4d4">The app is in testing on real equipment now. Ordering is not open yet, and prices will be published here before it opens. Each licence will be tied to your account email, so a lost or replaced phone does not cost you the licence.</p>
    <div class="actions"><a class="btn" href="/pricing.html">How ordering will work</a><a class="btn ghost" href="/support.html">Ask a question</a></div>
  </div>
</div></section>"""
    return page("home", "ServMod - service toolbox for maintenance engineers on Android",
        "ServMod reads, backs up and compares inverter parameters from an Android phone over USB-RS485. Hitachi, Allen-Bradley and Omron drives, label printers and more, fully offline.", body, "/")

def features():
    cards = [
     ("Inverters", "Hitachi WJ200 and WL200 over USB cable or USB-RS485, Allen-Bradley PowerFlex 520 and 525 on the DSI port, Omron 3G3MX2 over RS-485.", [
        "Read all parameters and keep the backup on the phone", "Restore a backup to the drive", "Compare a backup with the drive, or the drive with factory settings",
        "Edit a single parameter", "Run the motor manually from the Control screen", "Faults screen with causes and reset notes from the manual (Hitachi WJ200)"]),
     ("Printers", "Honeywell PM45 thermal label printers over a USB-Ethernet adapter.", [
        "Test the Ethernet port and test-print", "Keep your own printer list and test one or all", "PM45 fault guide: error alerts, front panel LEDs, print, network and RFID problems"]),
     ("PLC, read only", "Omron over FINS/UDP (port 9600) and Allen-Bradley Logix or Micro800 over EtherNet/IP (port 44818).", [
        "Per-machine list of items with live reading every second", "List of value changes you can copy", "No write function, by design", "Draft: tested on a simulator, not yet on a real PLC"]),
     ("Calc, Access, Notes, Parts", "Four small tools for the daily routine.", [
        "Calc: power, cable size, resistor colours, UK wiring colours, Ethernet pinouts", "Access: encrypted machine passwords", "Notes: service notes with annotated photos", "Parts: warehouse search with CSV and XLSX import"]),
     ("ESP32 Loader", "Flash ESP32, ESP32-S3 and CYD boards straight from the phone.", [
        "USB loader for .bin files with offsets", "MD5 verification and chip check", "Checked on a real ESP32 CYD board"]),
     ("Condition and Network", "Vibration and condition checks from the phone sensors, and network checks for the plant.", ["In field testing"]),
    ]
    sec = "".join(f'<section class="tight"><div class="wrap split"><div><h2 style="font-size:1.8rem">{t}</h2><p class="intro">{d}</p></div><ul class="rules" style="display:block;border:0;margin:0;padding:0;list-style:none">' + "".join(f'<li style="padding:12px 0;border-bottom:1px solid var(--line)">{x}</li>' for x in items) + "</ul></div></section>" for t, d, items in cards)
    body = f'<div class="wrap page" style="padding-bottom:0"><h1>Modules</h1><p class="intro">What each part of ServMod does today. Status labels are honest: release {APP_VERSION} is in testing, and modules marked draft have not been tried on live equipment yet.</p><div style="margin-top:26px">{status_legend()}</div></div>' + sec
    return page("features", "Modules", "Everything ServMod does: inverters, printers, read-only PLC, calculators, encrypted passwords, notes, parts search and an ESP32 loader.", body, "/features.html")

def equipment():
    drives = [("Hitachi WJ200 / WL200", "USB cable, or USB-RS485 adapter", "Yes", "Yes", "Yes"),
              ("Allen-Bradley PowerFlex 520 / 525", "USB-RS485 adapter on the DSI port", "Yes", "Yes", "Yes"),
              ("Omron 3G3MX2 (MX2-V2)", "USB-RS485 adapter (USB port later)", "Yes", "Yes", "Yes")]
    rows = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in drives)
    body = f"""<div class="wrap page">
<h1>Supported equipment</h1>
<p class="intro">Every drive uses the same screens: Backup, Parameters, Control, Settings and Faults.</p>
<h2 style="margin-top:48px;font-size:1.6rem">Inverters</h2>
<div class="scroll" style="margin-top:16px"><table class="tbl"><thead><tr><th>Drive</th><th>Connection</th><th>Read</th><th>Backup and write</th><th>Control</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="intro" style="margin-top:16px">More models and brands will follow. Tell us which drive you need on the <a href="/support.html">support page</a>.</p>
<h2 style="margin-top:56px;font-size:1.6rem">PLCs, read only</h2>
<div class="scroll" style="margin-top:16px"><table class="tbl"><thead><tr><th>Controller</th><th>Protocol</th><th>Notes</th></tr></thead><tbody>
<tr><td>Omron</td><td>FINS over UDP, port 9600</td><td>DM, CIO, W, H and A areas. Types WORD, INT, DWORD, DINT, REAL, BOOL.</td></tr>
<tr><td>Allen-Bradley Logix and Micro800</td><td>EtherNet/IP, port 44818</td><td>Read a tag by name. Optional CPU slot for Logix.</td></tr>
<tr><td>Mitsubishi</td><td>MC protocol</td><td>Planned. Usually needs a port opened in GX Works.</td></tr>
</tbody></table></div>
<p class="intro" style="margin-top:16px">Siemens is not supported: it needs the PUT/GET function unlocked in the controller. The PLC module is a draft and has been tested on a simulator only.</p>
<h2 style="margin-top:56px;font-size:1.6rem">Printers</h2>
<p class="intro" style="margin-top:12px">Honeywell PM45 industrial thermal label printers, over Ethernet through a USB-C Ethernet adapter.</p>
<h2 style="margin-top:56px;font-size:1.6rem">Adapters</h2>
<div class="prose"><ul>
<li><b>RS-485:</b> a USB-RS485 adapter with an FTDI, CP210x, CH34x or CH343 chip.</li>
<li><b>Ethernet:</b> any USB-C Ethernet adapter. Android handles it natively.</li>
<li><b>One USB-C port:</b> a phone has only one, so for Ethernet and RS-485 together use a powered USB-C hub.</li>
<li><b>CAN:</b> not supported yet.</li></ul></div>
<p class="intro" style="margin-top:20px">Wiring for each drive is on the <a href="/guides.html">connection guides</a>.</p>
</div>"""
    return page("equipment", "Supported equipment", "Inverters, PLCs and printers ServMod works with, plus the USB-RS485 and Ethernet adapters you need.", body, "/equipment.html")

def guides():
    body = """<div class="wrap page"><div class="prose" style="max-width:48em">
<h1>Connection guides</h1>
<p class="intro">Wire the drive to the phone with a USB-RS485 adapter. Bench-test before you touch a production machine.</p>
<h2>Omron 3G3MX2 over USB-RS485</h2>
<dl class="kv"><dt>Adapter A (D+)</dt><dd>to RS+ on the control terminals</dd><dt>Adapter B (D-)</dt><dd>to RS- on the control terminals</dd><dt>Defaults</dt><dd>Slave 1, 9600 baud, 8-N-1</dd><dt>Termination</dt><dd>Switch on the 120 ohm termination on the last drive</dd></dl>
<p>The RJ45 is for the remote operator only, not for ServMod. Changes to C071 to C075 apply after a power cycle.</p>
<h2>Hitachi WJ200 and WL200</h2>
<dl class="kv"><dt>Connection</dt><dd>USB cable from the inverter, or a USB-RS485 adapter on the RS-485 terminals</dd><dt>Defaults</dt><dd>Slave 1, 9600 baud, 8-N-1</dd></dl>
<h2>Allen-Bradley PowerFlex 520 and 525</h2>
<dl class="kv"><dt>Connection</dt><dd>USB-RS485 adapter on the DSI RJ45, pins 4 (TxRxD+) and 5 (TxRxD-)</dd><dt>Defaults</dt><dd>Node 100, 9600 baud, 8-N-1</dd></dl>
<p>The left RJ45 is EtherNet/IP and the right one is DSI.</p>
<h2>If the phone does not see the adapter</h2>
<ul><li>Use a data cable, not a charge-only cable, and an adapter with an FTDI, CP210x, CH34x or CH343 chip.</li>
<li>Confirm the USB permission prompt when it appears.</li>
<li>Check that slave number, baud rate and format in ServMod match the drive. A mismatch looks like no answer.</li>
<li>Swap A and B if the drive still does not answer. Labelling differs between adapters.</li></ul>
<p>Still stuck? Send the drive model and what the screen says through the <a href="/support.html">support form</a>.</p>
</div></div>"""
    return page("guides", "Connection guides", "How to wire Omron MX2, Hitachi WJ200/WL200 and Allen-Bradley PowerFlex 520/525 drives to the phone with a USB-RS485 adapter.", body, "/guides.html")

def pricing():
    body = """<div class="wrap page"><div class="split"><div>
<h1>Pricing</h1>
<p class="intro">Ordering is not open yet. The app is in testing on real equipment, and prices will be published on this page before the shop opens.</p>
<div class="actions" style="margin-top:28px"><a class="btn ghost" href="/support.html">Ask before you buy</a></div>
</div><div class="prose">
<h2 style="margin-top:0">How a licence will work</h2>
<ol>
<li>You order with your email address and create an account.</li>
<li>The app shows a Device ID. You enter it on your account page.</li>
<li>You receive an activation code by email, and it also stays on your account page.</li>
<li>If you lose or replace your phone, sign in and move the licence to the new Device ID.</li></ol>
<p>The code is checked inside the app, so ServMod keeps working with no internet connection.</p>
<h2>What stays the same</h2>
<ul><li>The app has no ads and no tracking.</li><li>Update checks only download a small version file.</li><li>Refund, VAT and licence terms will be final before ordering opens. Drafts are on the <a href="/refunds.html">refunds</a> and <a href="/licence.html">licence</a> pages.</li></ul>
</div></div></div>"""
    return page("pricing", "Pricing", "ServMod ordering is not open yet. How licences, activation codes and accounts will work.", body, "/pricing.html")

FAQ = [
 ("Do I need internet to use ServMod?", "No. Everything works offline. The app only goes online if you choose About, Check for updates."),
 ("Which phone do I need?", "An Android 7.0 or newer phone or tablet with USB host (OTG). Most phones from the last several years have it."),
 ("Which cable or adapter do I need?", "For drives, a USB-RS485 adapter with an FTDI, CP210x, CH34x or CH343 chip. For printers, a USB-C Ethernet adapter. See the connection guides."),
 ("Can it damage my equipment?", "Writing parameters or running a motor can make machinery move or stop unexpectedly. Back up first, check every written value and test on the bench before a production machine. Read the terms of use."),
 ("Does it work on iPhone?", "No. ServMod is Android only."),
 ("Will it support my drive or PLC?", "More models are planned. Tell us what you need through the support form. Tell us the exact model and the protocol, if you know it."),
 ("What if I lose my phone?", "Each licence will be tied to your account email. Sign in, enter the Device ID of the new phone and get a new activation code."),
]
def support():
    faq = "".join(f'<details><summary>{q}</summary><div class="a"><p>{a}</p></div></details>' for q, a in FAQ)
    body = f"""<div class="wrap page"><div class="split rev"><div>
<h1>Support</h1>
<p class="intro">Tell us what you were doing, which drive or printer it was and what the screen said. A short answer from you saves a long exchange.</p>
<form class="f" id="support-form" data-endpoint="/api/support" novalidate style="margin-top:30px">
  <div class="row"><div><label for="name">Name</label><input id="name" name="name" autocomplete="name" required></div>
  <div><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" required></div></div>
  <div><label for="topic">What is it about?</label><select id="topic" name="topic"><option>A question before buying</option><option>Problem connecting to a drive</option><option>Problem with a printer or PLC</option><option>Activation code or licence</option><option>A drive or device you want supported</option><option>Something else</option></select></div>
  <div><label for="info">Drive or device and app version</label><input id="info" name="info" placeholder="For example: Omron MX2, app 0.26"><div class="hint">Optional, but it helps.</div></div>
  <div><label for="message">Message</label><textarea id="message" name="message" required></textarea></div>
  <div class="hp" aria-hidden="true"><label>Leave empty<input name="website" tabindex="-1" autocomplete="off"></label></div>
  <div><button class="btn" type="submit">Send message</button></div>
  <div class="msg" id="form-msg" role="status"></div>
</form>
</div><div id="faq">
<h2 style="font-size:1.6rem;margin-bottom:18px">Common questions</h2>
{faq}
</div></div></div>"""
    return page("support", "Support", "Contact ServMod support and read answers to common questions about phones, adapters, drives and licences.", body, "/support.html")

def manuals():
    body = """<div class="wrap page"><h1>Manuals</h1>
<p class="intro">Search fault codes and parameters across the full manufacturer manuals. The app can open this page directly on the right code.</p>
<div class="f" style="margin-top:26px"><div class="row"><div><label for="mq">Search</label><input id="mq" type="search" placeholder="E04, F013, P-12, acceleration time" autocomplete="off"></div>
<div><label for="mm">Manual</label><select id="mm"><option value="">All manuals</option></select></div></div></div>
<div id="mres" style="margin-top:24px"></div>
<h2 style="font-size:1.4rem;margin:36px 0 12px">All manuals</h2><ul id="mlist"></ul>
<p class="hint" style="margin-top:24px">Manuals belong to their manufacturers. Links open the PDF at the page found.</p></div>"""
    return page("manuals", "Manuals", "Searchable PDF manuals for drives and devices: fault codes, parameters and wiring, linked from the ServMod app.", body, "/manuals/", extra_head='<script src="/manuals.js" defer></script>')

def doc(key, title, desc, path, inner, draft=True):
    note = '<div class="draft-note">Draft. This page will be completed and reviewed before ordering opens.</div>' if draft else ""
    body = f'<div class="wrap page"><div class="prose"><h1>{title}</h1>{note}{inner}</div></div>'
    return page(key, title, desc, body, path)

TERMS = """<p>ServMod is professional diagnostic and programming software for use by qualified, experienced technicians. It can change parameters of connected equipment, such as inverters, start and stop motors, and read from controllers. By using this application you confirm and agree that:</p>
<ol>
<li>You are a competent person who understands variable frequency drives, the connected machinery and the manufacturer's documentation, and you will follow the applicable safety rules and regulations at your site.</li>
<li>Starting a motor or changing parameters can cause machinery to move unexpectedly, damage equipment, stop production or injure people. You must make sure that the machine, the area around it and the people near it are safe before you do either.</li>
<li>You will make and check a backup of the equipment parameters before writing anything. You are responsible for verifying every written value on the drive.</li>
<li>You use this software entirely at your own risk. It is provided "as is" with no warranty of any kind, express or implied, including fitness for a particular purpose and accuracy of parameter data.</li>
<li>To the maximum extent permitted by law, the author, Dariusz Grabowski, accepts no liability for any damage, loss, injury, downtime, data loss or warranty claims arising from the use or misuse of this software. Nothing here limits liability that cannot be limited by law.</li>
<li>This is an independent tool. It is not made, approved or supported by Hitachi, Omron, Rockwell Automation or any other manufacturer. Product and company names belong to their owners. Using it may affect your equipment's manufacturer warranty.</li>
<li>This software and its data may not be copied, redistributed or reverse engineered without the author's written permission.</li>
</ol>
<p>ServMod is not a safety function and must never be used as an emergency stop.</p>"""
PRIVACY = """<h2>The app</h2><p>ServMod works offline. It does not send your parameter backups, printer lists, notes, passwords or any other data anywhere. Everything stays on your phone unless you choose to share a file yourself.</p>
<p>The Device ID shown in the app is a code derived from your phone. It is used only to create your activation code. The update check downloads one small file and sends no identifier.</p>
<h2>This website</h2><p>The site uses no advertising cookies and no analytics scripts. Fonts are served from this site, not from a third party. Cloudflare delivers the site and may process technical request data such as IP address to protect and speed it up.</p>
<h2>Support messages</h2><p>If you write to support, we keep your name, email address and message to answer you and to help with later questions.</p>
<h2>Ordering</h2><p>When ordering opens, we will store your email address, your Device ID and your order details to issue and re-issue your activation code and to handle payment, tax and support. Card and PayPal payments are handled by the payment providers, and we do not see your card details. This section will be completed with the full list of providers, retention periods and your rights before ordering opens.</p>
<h2>Contact</h2><p>The controller of the data is Dariusz Grabowski, United Kingdom. Contact: <a href="mailto:support@servmod.com">support@servmod.com</a>.</p>"""
REFUNDS = """<p>This is a plan for how refunds will work, not final terms.</p>
<h2>Digital delivery</h2><p>ServMod is delivered digitally and the activation code is issued straight after payment. UK and EU consumers can normally cancel a digital purchase within 14 days, unless they agree that delivery starts at once and acknowledge that they lose the right to cancel once it has started. The final checkout wording will say exactly this.</p>
<h2>If it does not work for you</h2><p>If the app does not work with your equipment, contact support within 30 days of purchase and describe the problem. We will try to fix it or, if we cannot, refund you.</p>
<h2>Lost or replaced phone</h2><p>This is not a refund case. Move your licence to the new Device ID from your account page.</p>"""
LICENCE = """<p>This is a plan for the licence terms, not final terms.</p>
<h2>What you get</h2><p>A personal, non-transferable licence to use ServMod on one Android device at a time. The licence is tied to your account email, not to one phone.</p>
<h2>Activation</h2><p>An activation code is created from your Device ID and signed. The app checks the signature offline. You can move the licence to a new Device ID from your account page if the old phone is lost, broken or replaced.</p>
<h2>Updates</h2><p>Updates are published on this site and the app can check for them from About, Check for updates. Which updates are included in the price will be stated before ordering opens.</p>
<h2>Not allowed</h2><p>Copying, redistributing, sharing activation codes or reverse engineering the app. See also the <a href="/terms.html">terms of use</a>.</p>"""

def not_found():
    body = '<div class="wrap page"><div class="prose"><h1>Page not found</h1><p class="intro">That page does not exist. Try the <a href="/">home page</a>, the <a href="/features.html">modules</a> or the <a href="/support.html">support page</a>.</p></div></div>'
    return page("", "Page not found", "This page does not exist.", body, "/404.html", noindex=True)

PAGES = {
 "index.html": home(), "features.html": features(), "equipment.html": equipment(), "guides.html": guides(),
 "pricing.html": pricing(), "support.html": support(),
 "terms.html": doc("", "Terms of use", "Terms of use and safety disclaimer for ServMod.", "/terms.html", TERMS, draft=False),
 "privacy.html": doc("", "Privacy", "What ServMod and servmod.com do and do not collect.", "/privacy.html", PRIVACY),
 "refunds.html": doc("", "Refunds", "How refunds for ServMod will work.", "/refunds.html", REFUNDS),
 "licence.html": doc("", "Licence", "How the ServMod licence and activation will work.", "/licence.html", LICENCE),
 "manuals/index.html": manuals(),
 "404.html": not_found(),
}

def main():
    # build into OUT, keep the update feed dir untouched (server side)
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        p = os.path.join(OUT, f)
        if f == "servmod": continue
        if f in ("fonts", "assets"): continue
        if os.path.isfile(p): os.remove(p)
    for name, content in PAGES.items():
        os.makedirs(os.path.dirname(os.path.join(OUT, name)), exist_ok=True)
        open(os.path.join(OUT, name), "w", encoding="utf-8").write(content)
    shutil.copy(os.path.join(HERE, "style.css"), os.path.join(OUT, "style.css"))
    shutil.copy(os.path.join(HERE, "manuals.js"), os.path.join(OUT, "manuals.js"))
    shutil.copy(os.path.join(HERE, "site.js"), os.path.join(OUT, "site.js"))
    urls = [("/", "1.0")] + [(f"/{n}".replace("index.html", ""), "0.7") for n in PAGES if n not in ("index.html", "404.html")]
    open(os.path.join(OUT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{DOMAIN}{u}</loc><lastmod>{TODAY}</lastmod><priority>{p}</priority></url>\n" for u, p in urls) + "</urlset>\n")
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nDisallow: /servmod/\nSitemap: {DOMAIN}/sitemap.xml\n")
    print("built", len(PAGES), "pages ->", OUT)
main()
