# ServMod website – project index (read this first)

Last updated: 2026-11-28. Keep this file current: when something is added/changed/learned, update it in the same commit.
Mirror on the PC: `C:\Users\grabo\Desktop\Arduino\ServMod\handoff\website\` (copy of `docs/`). Master copy = this repo.

## What it is
Static marketing site + small FastAPI backend for **ServMod** (Android toolbox for maintenance engineers), live at https://servmod.com. Site and app GUI are **English only**; the owner (DG) talks Polish.

## Repo map (github.com/darek791/servmod-site, branch `main`)
| Path | What |
|---|---|
| `src/build.py` | Generates every HTML page into `site/` (header/nav/footer template in `page()`, one function per page: home, features, equipment, guides, pricing, support, manuals, account, legal docs, 404). **Edit here, never the generated HTML.** |
| `src/style.css`, `src/site.js`, `src/account.js`, `src/manuals.js` | Styles and scripts, copied to `site/` by build. `site.js` = menu, support form, "Sign in/My account" header label. `account.js` = login + dashboard + admin. `manuals.js` = fault-code search. |
| `site/` | **Generated output, committed** (server publishes this). Always run build before commit. `site/assets`, `site/fonts` are hand-maintained (not regenerated). |
| `manuals_src/data/*.json` | Fault-code / parameter data (wj200, pf520, fc280, mx2) -> `site/manuals/data.json`. Own-words rewrites only; no manufacturer PDFs hosted. |
| `backend/servmod_api/` | FastAPI app: `app.py` (routes), `core.py` (SQLite, sessions, rate limit), `licence.py` (signs activation codes), `mail.py` (log/Resend/SMTP). Tests: `backend/tests/test_api.py`. |
| `nginx/servmod.conf` | Full nginx server config (auto-applied by sync, validated with `nginx -t`, rolled back if rejected). |
| `server/` | `servmod-sync.sh` (the 1-minute deploy job), `servmod-api.service`, bootstrap/repair scripts. |
| `tools/` | `release.py` (publish signed APK to update feed), `install_backend.cmd/.ps1` (one-time server setup from the PC). |
| `docs/` | This index + `HOW_WE_WORK.md`. |

## Pages (URL -> builder in build.py)
`/` home · `/features.html` modules · `/equipment.html` · `/guides.html` connection guides · `/manuals/` fault codes · `/pricing.html` (no shop yet) · `/support.html` (form -> `/api/support`) · `/account/` (login by e-mail link/6-digit code, no passwords) · `/licence.html`, `/privacy.html`, `/terms.html`, `/refunds.html` · `404.html`. Header has an always-visible **Sign in / My account** button (`#acct-link`).

## Backend API (`/api/*`, proxied by nginx to 127.0.0.1:8100)
Public: `GET /api/health`, `GET /api/latest.apk` (302 to newest APK in feed; 404 while none published), `POST /api/support` (valid e-mail, message 10-5000 chars, rate-limited, stored as ticket + mailed to SUPPORT_TO or first ADMIN_EMAIL).
Auth: `POST /api/auth/request|verify|logout`. Account: `GET /api/me`, `POST /api/devices` (Device ID -> activation code), `POST /api/devices/release`, `GET /api/me/export`, `DELETE /api/me`.
Waiting list: REMOVED 2026-11-20 (no endpoints, no page, table dropped at start). Admin (ADMIN_EMAILS only): `/api/admin/overview|grant|revoke|ticket|request`.
All POST/DELETE need header `X-Requested-With: servmod` and same-origin. SQLite tables: users, login_tokens, sessions, entitlements, licences, tickets, rate, audit.

## Infrastructure
- Domain servmod.com on Cloudflare DNS -> Hetzner server (167.233.108.235; the box formerly ran the trading bots – bot files still there, do not delete without asking). nginx + certbot TLS.
- Server paths: site `/var/www/servmod/`, **update feed** `/var/www/servmod/servmod/` (never touched by sync), backend `/opt/servmod-app`, data `/var/lib/servmod` (SQLite), licence signing key `/etc/servmod/license_private.key`, repo checkout `/var/lib/servmod-repo`, sync log `/var/log/servmod-sync.log`.
- Mail: Resend (MAIL_MODE=resend, key in server env, never in repo); inbound support@servmod.com via Cloudflare Email Routing (delivery confirmed 2026-10-11).
- Update feed: `/servmod/version.json`, `/servmod/beta/version.json`, `/servmod/history.json`, `/servmod/releases/*.apk`. **APK download is open (unlocked 2026-10-26); published stable is 0.99.55 (versionCode 430, feed version.json).**

## Current status / open items
- 2026-10-15 content refresh to app 0.55: `APP_VERSION` 0.55, `MODULES` list now 17 tools (added Tools, USB Tools, NFC & Barcode, Zodiac Printers, ServMod Box, Steppers, My Stuff; Danfoss FC 280 in Inverters; Printers cable check), features/equipment/guides updated (Hitachi: WL200 USB ok, WJ200 via RS-485 only). When the app gets new modules, edit `MODULES`, the `features()` cards and `equipment()`/`guides()` in src/build.py.
- Done: full static site, manuals search, account login, support form (works), licence activation codes, visible Sign-in button.
- (Waiting list was removed 2026-11-20.)
- Not done: shop/cart/payments (Stripe + PayPal, reuse engine from qubivibe.com – waiting for the owner to show those files), automatic licence e-mail after purchase. (APK is published and downloadable.)
- Known gotcha: do not reuse DOM id `acct` (account page uses it) – header link is `acct-link`.


## 2026-10-17 content refresh for app 0.60 (commit b9582c2)
- `APP_VERSION` = 0.60, MODULES = 18 (added Backup; ServMod Box now 'In field testing').
- Features: Backup card, USB Tools fake-size/recover, Box description; equipment table: Hitachi WJ-C1 via Box; privacy: Backup writes an encrypted copy to a user-chosen cloud folder.
- Status source for the site: `_komunikacja/STATUS.md` (mirror docs/komunikacja/). On a new app/firmware version: update build.py MODULES and features cards, build, push.

- 2026-10-18: removed the bio section from the home page; new page About (`about()` in build.py, nav item 'About', /about.html) with a short bio (30 years: moulding, petrochemicals/refineries, robotics, cars, food production and fast packing lines, solar panels). Home keeps a short 'Ordering' block.

- 2026-10-25: personal name removed from the site and docs; the author is shown as "DG" (footer, About, Terms, Privacy). Future wording: "we"/team. Note: Privacy/Terms name the controller as "DG, United Kingdom" - before sales open these need the proper trading name and address (UK rules for businesses selling online).

- 2026-10-25 (APP-011): content refreshed to app 0.75: 20 modules (+Thermocontrollers, OBD2 Draft), equipment table now Drive/Connection/Status (tested vs not yet tried), plans Free/Pro/Subscription described on Pricing (no prices yet), brand strip and disclaimer extended. Tested on hardware per handoff `servmod-hardware-verified.md`: WL200, WJ200/C1 (via Box), PowerFlex 525, FC 280, VLT 2800, Lenze 8400.

- 2026-10-25: shop built but CLOSED by default: `backend/servmod_api/shop.py` (Stripe Checkout + signed webhook `/api/pay/stripe`, idempotent `orders`, auto-issue of codes via `issuing.py`), pricing page shows buy buttons only when `/api/shop/config` says open. Setup and rules: `docs/PAYMENTS.md`. Owner decision: main licence key lives on the server (`/etc/servmod/license_private.key`), Stripe first, PayPal inside Stripe if possible.

- 2026-10-25: Privacy now describes real shop data (email, Device ID, code, order record; Stripe handles cards; no customer files kept), Licence page describes Free/Pro/Subscription. Terms/Refunds/Licence still carry the 'Draft' banner until the owner accepts. Owner decision: no business registration until sales approach GBP 1000 (check HMRC trading allowance and the ICO data protection fee when the first sale happens).

## 2026-10-25 – Shop tested in Stripe sandbox
- Webhook `servmod-site` (sandbox Qubivibe) -> /api/pay/stripe; keys installed on the server with install_payment_keys.cmd (test keys); shop open in TEST mode.
- Test purchase of Pro with card 4242 OK: receipt e-mail sent from no-reply@servmod.com (no Device ID entered, so e-mail has sign-in steps).
- Fix: CSS/JS now get ?v=<hash> (build.py) because Cloudflare/browser cached an old site.js for 4 h. Pricing hides "not open yet" text when the shop is open.
- TODO before real sales: live keys + live webhook, decide separate Stripe account, PayPal check, confirm prices, legal drafts, home page "Ordering" block text, test with Device ID (code in e-mail) and refund path.

## 2026-10-25 – Purchase from the app
- /api/shop/checkout accepts device_id + claim; new GET /api/shop/claim (pending/ready/error). Test added (14 tests pass). Task WWW-001 sent to APP. Thank-you page text differs when the buyer came from the app (#paid=app).

## 2026-10-25 – PayPal
- Separate PayPal integration (Orders v2, capture on return) next to Stripe; keys via tools/install_paypal_keys.cmd; site shows card and PayPal buttons when both on. 16 backend tests pass.

## 2026-10-26 – PayPal tested in sandbox
- PayPal sandbox keys installed (app "ServMod", Merchant); buttons live on Pricing; test purchase of Pro from the website with a sandbox buyer OK (capture + thank-you view). Pending: PayPal button in the app (WWW-003), live keys for Stripe and PayPal.

## 2026-10-26 – Launch wording
- Refunds, Licence, Privacy and Terms rewritten as final (Draft banner removed on the owner's instruction; not legal advice): 14-day cancellation waiver for digital content, 30-day "does not work" refund, one-year Subscription without auto-renew, "Buying a licence" section in Terms. Checkout consent text (Stripe and under the site buy buttons).
- Home "Ordering" block and Pricing "How a licence works" describe buying from the app; download is live since 2026-10-26.
- Stripe LIVE (restricted key, Checkout Sessions Write) and PayPal LIVE keys on the server; tools/set_prices.cmd changes prices only.

## 2026-10-26 – Images and Requests page
- Home hero = three real app screenshots in phone frames on a factory background (ComfyUI SDXL backgrounds on the owner's PC; screenshots composited with Pillow). New "In the app" gallery (6 cards, site/assets/app/). Bench photos stay in Connection guides only. New "Cables and adapters" section in Connection guides (site/assets/adapters/: OTG, USB-A mini/micro, USB-C to USB-B, USB-RS232). Still missing: a clean photo of the USB-RS485 adapter.
- New page /requests.html: form for drives, protocols and features customers need (POST /api/requests, table `requests`, e-mail to SUPPORT_TO/admin, rate-limited, honeypot, e-mail optional). Admin panel lists requests with status new/planned/done/declined (POST /api/admin/request). Privacy page mentions requests. 17 backend tests pass.
- Web-only endpoint, not used by the app; KONTRAKT.md unchanged.

## 2026-10-26 – Download unlocked (owner said "unlock")
- New /download.html: "Download free version" button (/servmod/latest.apk), version/size/SHA-256 read from /servmod/version.json, 4 install steps (unknown sources, Play Protect "Install anyway"), fallback with a link to the waiting list while the feed returns 404. Visible "Download" button in the nav, hero ("Download free for Android") and a home section; footer links Download and Update news. Waiting list kept as "Update news".
- Hero slogan changed to "Fix it faster. The app remembers for you."
- APK to publish: ServMod-0.76.3-clean.apk (versionCode 198, com.servmod.app, not debuggable, signed with the owner's own certificate, valid to 2056). Publishing is done by the owner on the PC: web\install_backend\publish_release.cmd (dry run first, then types PUBLISH). Until then the feed is 404 and the download page shows the waiting-list fallback.
- After publishing: check https://servmod.com/download.html, then close APP-014 in inbox/WWW.md. Waiting-list e-mail only from the admin panel and only with the owner's consent.

## Visit counter (2026-10-26)
- Own cookie-free counter: `site.js` posts `/api/hit` (page, referrer host, view or download click); table `hits` (day, path, event, daily salted hash of IP+browser, no IP stored). Bots and the admin's own browser (localStorage `sm_me`) are skipped. Admin panel has a "Visits" section: today/7/30 days, 14-day bar chart, top pages, referrers. Privacy text updated. Real visitor IP from `CF-Connecting-IP`.

## General diagram (2026-11-02)
- Home page section `#how` "How it connects" (DIAGRAM in build.py): phone with ServMod -> adapter / Box / USB / network -> equipment. Pure HTML/CSS, stacks on phones.

## Wiring diagrams page (2026-11-02)
- `/wiring.html` (WIRING list + wiring_page() in build.py): all 46 wiring diagrams copied from the app (`wl200_android/app/src/main/assets/wiring/*.webp`) into `site/assets/wiring/`, grouped by device with chips, status badge (Tested on a drive / Not yet tried / Draft) from servmod-hardware-verified. Left out: lenze8400_2_usbcan (COMING SOON). Linked from Guides, Equipment, footer and the home diagram. When the app adds or changes diagrams: copy the webp files again and update WIRING.

## Device pages for search (2026-11-02)
- 18 landing pages `/equipment/<slug>.html` generated from `src/devices.py` (DEVICES list: name, status T/N/D, ways to connect, facts, wiring files). Each has its own title/description, H1 "<device> parameter backup and restore from an Android phone", BreadcrumbList JSON-LD, wiring diagrams, what is free vs Pro, canonical URL; all in sitemap.xml. Linked from Equipment (Device pages list) and from the Wiring page (Device page button). Facts only from app docs, diagrams and servmod-hardware-verified; when a drive gets tested change `st` in devices.py.
- Google Search Console: add property servmod.com (DNS TXT verification, done by the owner), then submit https://servmod.com/sitemap.xml.

## What's new page and site check (2026-11-02)
- `/whats-new.html`: release notes. A static copy of 0.76.3 is built in; `site.js` replaces it with the stable entries of `/servmod/history.json` (written by tools/release.py). Linked from the footer and the Download page. History entries need clear English `notes`.
- Local check of all 37 pages: no broken internal links, no missing alt text, unique titles and descriptions, LCP under 0.5 s on a mobile viewport. Not measured on the live site (not reachable from the container).

## Build your own ServMod Box (Pro only), added 2026-11-05
- Page `/modbox.html` (src/build.py `modbox()`, src/modbox.js). Public text; wiring drawings and firmware are loaded by JS from the API only when the caller is Pro. States: not signed in -> sign-in prompt, signed in without Pro -> pricing prompt, no files on server yet -> "being prepared".
- Backend `backend/servmod_api/box.py` (tests: `test_box_*`). Files in `BOX_DIR` (default `/var/lib/servmod/box`, NOT the public web root): `firmware.json`, `firmware/*.bin`, `schematics/*`.
  - `GET /api/box/firmware` -> manifest from BOX (version, per-file sha256/bytes/offset/flash size, `url`) plus `schematics` list.
  - `GET /api/box/firmware/<file>` -> .bin download (only files named in the manifest), `GET /api/box/doc/<file>` -> drawing.
  - Pro check on the server: session cookie with a non-revoked entitlement containing `PRO` or `ALL` (Subscription alone is not Pro), or header `X-Licence: <activation code>` (signature valid, device not released, entitlement not revoked and Pro). Downloads are written to the audit log (`box-fw`, `box-doc`).
- Upload to the server: `tools\publish_box_firmware.cmd` on the PC (checks sha256 and sizes against firmware.json, asks for PUBLISH). New firmware from BOX: same folder `ServMod\handoff\www_assets\box_firmware`, run the tool again.
- Linked from Pricing (plans table row) and from the account page for Pro accounts. Mini build is labelled experimental, "not flashed yet".
- Not verified live (server not reachable from the container); local test with real files and a Pro session passed.

## Content refresh to app 0.99.42, 2026-11-16
- (Superseded 2026-11-17: published app is now 0.99.52 and the "next release" marks are gone.)
- MODULES: added Setup (Draft), EzSQ programs (In field testing), Bilwinco boards (In field testing); Siemens OP17 now In field testing (spare panels); Tools mentions Nameplate; ESP32 Loader mentions Box firmware download (Pro).
- Features cards: Setup and drive converter, EzSQ programs, Bilwinco boards and OP17. Equipment: Hitachi SJ200, Danfoss FC 302 (partly tested), Mitsubishi FR-E800 (tested by owner), WJ-C1 direct USB works, PF525 also through the Box, Lenze USB-CAN planned; new table "Control boards and panels".
- Privacy: Nameplate "Read with AI" sends the photo to Google Gemini with the user's own key (stated explicitly; app otherwise offline).
- Box firmware on /modbox.html stays 0.9.1: BOX firmware 0.9.2 (Danfoss HID on USB host, contract 1.7) is not compiled or tested, so not published. Source of truth: `_komunikacja/STATUS.md`.
- When the owner publishes a new APK: bump `APP_VERSION`, drop the "next release" marks for what shipped.

## Pinterest, started 2026-11-17
- New business profile "Servmod.com" (@servmodpins), created by DG on a separate login. Domain servmod.com claimed and verified (meta `p:domain_verify` in the head of every page, set in `src/build.py`, commit 7eeae61).
- Pin texts for 7 app and site screenshots: `pinterest_pins.csv` (title, description, alt, board, destination URL with UTM `utm_source=pinterest`). Nameplate, Setup and EzSQ screens can now be added, with Draft / untested wording.
- Traffic from Pinterest shows in the admin "Visits" panel as a referrer.
- Open: per-page `og:image`, Rich Pins, boards and first pins (DG).

## SEO: fault-code and parameter pages, 2026-11-17
- New `src/faults.py` builds static, indexable pages from `manuals_src/data/*.json` (our own summaries with manual page numbers): `/fault-codes/` hub, `/fault-codes/<drive>/` (WJ200, FC 280, MX2, PowerFlex 520) and one page per code (175), plus `/parameters/<drive>/` lists. Site is now 222 pages, sitemap 220 URLs (checked live, HTTP 200).
- Internal links: nav "Fault codes" now points to `/fault-codes/`; device pages link to their fault hub; `/manuals/` (search tool) lists static links; every fault page links to the device page, wiring and download.
- Each page has its own title and description, BreadcrumbList JSON-LD, and the standard disclaimer. No duplicate titles or descriptions across the site.
- Pinterest: tool `pinterest_servmod.js` (menu option PS in AI Business System) pins from `C:\ComfyUI\servmod_pins\pinterest_pins.csv` (52 pins: app screenshots and 42 wiring diagrams). Domain claimed and verified.
- Next ideas: fault pages for Lenze 8400, Mitsubishi and Hitachi WL200 once we have data; Google Ads on narrow model queries; submit the new sitemap in Search Console (already known to Google).

## 2026-11-17 – Corrections: download live, app 0.99.52
- Download has worked since 2026-10-26 (earlier notes saying "locked" were stale). Published stable app = 0.99.52 (versionCode 427, feed /servmod/version.json).
- Site content now matches app 0.99.52 (APP_VERSION in src/build.py); all "next release" wording removed. Honest labels kept: Setup = Draft; Nameplate, Bilwinco and EzSQ untested on hardware unless APP confirms otherwise (task WWW-006).
- /servmod/latest.apk: backend falls back to the public /servmod/version.json when it cannot read the feed directory (it returned 404 before). Live check pending after deploy.

## 2026-11-17 – Home simplified, Subscription only for Pro owners
- Home: hero badge "Read. Back up. Compare. Write."; module table (25 tools, with Draft/bench statuses) moved from Home to Modules (`/features.html`); Home has "Tested on real drives" (devices with `st == "T"` in devices.py) and links to Equipment and Modules. Gallery has only drive-related shots.
- Owner decision: Pro price unchanged; Subscription (GBP 20/year) is an add-on for Pro owners only. Backend `shop.py`: `/api/shop/checkout` with product `sub` returns 403 + readable `detail` unless the caller is signed in with Pro/ALL or the Device ID holds an active Pro licence (`_owns_pro`). A payment that already arrived is never refused in `fulfil`. Test `test_subscription_only_for_pro_owners` (22 tests). `site.js` shows the server's `detail` on checkout errors. Task WWW-007 sent to APP (app buy screen).
- Open from the Grok review (docs/ review of 2026-11-17): fix "Nothing leaves the phone" wording (Nameplate sends a photo to Gemini with the user's own key; Backup can use a cloud folder); static "Ordering is not open yet" / "Prices will be published" text in pricing HTML; Box is shown equal to the cable in "How it connects"; hero screenshots have errors (FULL badge, different clocks, cut "Parameters"). Name and photo on the site: owner postponed.

## 2026-11-17 – Offline wording made accurate
- Owner decision: Nameplate (photo to Google Gemini, own key) stays. Home hero "Works offline, no account needed"; "Careful by design" card is now "Offline by default" and names the two optional online features (cloud Backup folder, Nameplate); FAQ and meta description adjusted. Privacy page already stated the Gemini exception. Task WWW-008 to APP: first-use warning in Nameplate; offline on-device reading is a later idea.

## 2026-11-17 – Breadth restored on Home
- Owner: after the Grok-driven cleanup the home looked like a drives-only app, while the price rests on the breadth of the toolbox. Home now: hero badge "One app. {N} tools." (N = len(MODULES)), "Tested on real drives", then a new section "And a whole toolbox beside the drives" with 6 grouped cards, each with an honest status chip (Ready / In field testing / Draft); gallery has the tools home screen and resistor calculator again. The full module table with statuses stays on Modules.

## Gallery and hero refreshed (2026-11-17)
- Home gallery "In the app" split into **Drive work** (inv, backup, lenze, converter, setup, nameplate) and **The toolbox** (home, tools, solar, plc, nfc, wiring, resistor). New cards `site/assets/app/card-{converter,setup,nameplate,tools,solar,plc,nfc}.jpg` (900x1125, status bar cropped) made from the owner's Drive "Pinterest" screenshots.
- Draft labels in captions: Drive converter, Setup, PLC emulator, NFC labels. Nameplate caption says optional AI, check values.
- `hero-app.jpg` rebuilt: Inverters list, Tools grid, Setup (no FULL badge, no mismatched clocks), over a blurred factory-hall background (ComfyUI servmod_bg3).
- Screenshots with third-party names/MACs (Condition, Network, Devices) deliberately not used.
- Modbox page carries the "both Boxes run 0.9.2, files offered still 0.9.1" notice until BOX delivers the bins (WWW-009).

## /servmod/latest.apk fix (2026-11-17)
- Cause (likely): the API fallback fetched https://servmod.com/servmod/version.json with the default Python user agent, which Cloudflare blocks; the file read itself failed for the service user. Fixes: (1) `servmod-sync.sh` now makes symlink `/var/www/servmod/servmod/latest.apk` -> newest APK on every run (`mklatest`), (2) nginx serves that symlink directly (attachment `ServMod.apk`) and only falls back to the API, (3) API fallback sends a User-Agent and logs why it failed.

## Customer chat assistant (built 2026-11-19, OFF until the owner runs the setup)
- Backend `backend/servmod_api/chat.py`: `GET /api/chat/status`, `POST /api/chat` (needs `X-Requested-With`). Answers only from `knowledge.json` (generated by `src/build.py`: tools, devices, FAQ, pricing/refunds/licence page text, 175 fault codes; the fault entry named in the question is added). Limits: 20 questions/h and 60/day per IP, 400/day overall (`CHAT_DAILY_MAX`), 600 chars, 6 turns. If the LLM is unreachable the user gets an "offline, use Support" answer.
- LLM = owner's Ollama (qwen2.5:14b on the RTX 3060, GPU1) behind `tools/chat_gateway.py` (key check, fixed model, output limits) on 127.0.0.1:11500 and a Cloudflare Tunnel `llm.servmod.com`. Config `CHAT_URL`, `CHAT_KEY`, `CHAT_MODEL` in `/etc/servmod/pay.env`; without `CHAT_URL` no widget is loaded (`site.js` asks `/api/chat/status`, then loads `chat.js`).
- Owner steps on the PC: `tools\chat_pc_setup.cmd` (key, cloudflared, tunnel, autostart tasks), then `tools\install_chat_keys.cmd` (server config; `install_chat_keys.cmd OFF` switches it off). Key file `tools/chat_key.txt` is git-ignored.
- Privacy page has a "Website assistant" section. 23 backend tests pass.

## Box firmware 0.9.2 prepared (2026-11-19)
- Owner supplied the two merged images (DevKit 16 MB, mini 4 MB; both contain "0.9.2"). WWW trimmed the empty flash end (full = bootloader+partitions+app up to the end of the app, rounded to 4 KB, 1773568 B each), cut the app-only files at 0x10000 from the same images and checked the embedded application SHA-256. Files + `firmware.json` (version 0.9.2, build_date 2026-11-19, new `changes` text shown on /modbox.html) are in `ServMod\handoff\www_assets\box_firmware`; old manifest kept as `firmware.json.bak_0.9.1`.
- NOT yet on the server: the owner must run `tools\publish_box_firmware.cmd` (PUBLISH). Danfoss FC 302 over the Box is stated as not confirmed on a drive; the "experimental" label of the mini was removed on the owner's word (2026-11-19: the mini works).
- Modbox page notice now says the offered version is shown at the top of the download block.

## Website chat changes (2026-11-19/20)
- Chat answers in English only (retry once if the model drifts into Chinese/Japanese/Korean, then a fixed fallback). `APK_FACTS` added to the facts; rule "never claim security audits, virus scans or certificates". Answers up to ~180 words, `num_predict` 500. New `POST /api/chat/warm` (needs `X-Requested-With`; 6/h per IP, 1 per 240 s overall) sends a one-token request so the model is loaded when the chat window is opened (`chat.js`). 23 backend tests pass.

## Privacy and data deletion pages (2026-11-20, for Google Play)
- `/privacy.html` (website + version downloaded from servmod.com): corrected (update check sends the app version, accurate network list), links to the two new pages.
- `/app-privacy.html`: app installed from Google Play only. No accounts/ads/analytics; network = Box firmware download (licence key), optional Gemini photo with the user's own key, local network. No prices, purchases, Pro or Device ID wording. Permissions explained (camera, microphone, location/Bluetooth/Wi-Fi, NFC, USB, files). Use this URL in Play Console.
- `/delete-data.html`: app data lives on the phone (clear data/uninstall); account deletion on /account/, waiting-list unsubscribe, e-mail to support@servmod.com; orders kept as long as accounting rules require. Use this URL for the Play data-deletion field.
- Footer Legal list has both new links. Controller shown as "DG, United Kingdom" (owner has postponed the full name). `terms.html` NOT changed: still marked Draft and still describes selling on the site; owner decision pending. All three pages await owner approval. Closed APP-024 and APP-025 in inbox/WWW.md.

## Waiting list removed (2026-11-20)
- Owner: nobody was on the list, remove everything. Gone: `/waitlist.html`, forms and links, account checkbox, admin send block, `/api/waitlist*`, `/api/admin/waitlist/notify`, table `waitlist` (`DROP TABLE IF EXISTS` in `core.py`). 21 backend tests pass.

## Content refresh APP-027 (2026-11-24)
- `APP_VERSION` = 0.99.55 (the version in the feed; the old 0.99.52 was already stale). Items newer than the download carry "Next release" and "not yet tried": Danfoss FC 51 (device page `/equipment/danfoss-fc-51.html`, Equipment row "Partly tested", 2 drawings), Setup layouts for VLT 2800 and FC 302, Parts FIND BY PHOTO. VLT 2800: 2 new front-DB9 drawings (pin 8 = P, 9 = N, 3 = GND) and test wording (read, write, restore, factory reset, adapter and Box). Wiring page now has 50 drawings.
- Privacy and app-privacy mention the optional Gemini photo search in Parts.
- Not added (no description from APP, asked in WWW-011): Werma, Thumb wheel, Terminals from backup, Zodiac -> ICE rename, WL200/WJ200 power from physical registers.

## Content refresh finished, FC 302 (2026-11-26)
- APP-027 closed: new module rows Werma, Charger, Appearance (thumb wheel + language) and "ICE printers (Zodiac)" (all Draft, "Next release"); Terminals sketch sentence in Inverters; privacy lists Setup photo next to Nameplate/Parts. Danfoss FC 302 through the Box confirmed by the owner (Equipment row; `firmware.json` in handoff updated, needs `publish_box_firmware.cmd` again).

## Google Play Billing redeem (2026-11-26, APP-031, NOT DEPLOYED)
- Code is on branch `play-billing` (commit ced9c30), not on `main`, so the server does not run it. `backend/servmod_api/playbilling.py` + table `play_purchases`; 25 tests pass with a fake Google. `POST /api/shop/play/redeem` per KONTRAKT 1.8: Google answers decide product/package/state, acknowledge before the code, 3 devices per purchase chain (linkedPurchaseToken), rate limits, daily Voided Purchases check (revokes). Without `PLAY_KEY_FILE` it answers 503 (dry run).
- Codes come from `issuing.issue()`: one entitlement (source `play`, 3 seats) per purchase chain on a synthetic user `play-<hash>@play.invalid`, so the Box firmware Pro check and revoking work as for shop licences.
- To go live (owner): Google Cloud service account + link in Play Console, key file on the server only (`PLAY_KEY_FILE` in `/etc/servmod/pay.env`), then merge `play-billing` into `main`. Open points for APP: 3-day subscription grace vs "no extra days" in the contract text, a device can get two codes (PRO and SUB), IN_GRACE_PERIOD treated as inactive.

## Play Billing, merged to main (2026-11-27, APP-032)
- Branch `play-billing` (head c0b4790) now also has `tools/install_play_key.cmd/.ps1`: copies the service-account JSON from the PC to `/etc/servmod/play-key.json` (root:servmod, 640; the unit runs as `servmod` with `/etc/servmod` read-only), sets `PLAY_KEY_FILE` in `/etc/servmod/pay.env`, restarts `servmod-api` (needed: the Voided Purchases thread starts only when a key exists) and smoke-tests redeem (400 = Google answered, 503 = key not usable).
- Play Console data: package `com.servmod.app`, `servmod_pro` (one-time, option `buy`), `servmod_sub` (base plan `yearly`). Code reads sub from subscriptionsv2 by token and picks the lineItem with productId `servmod_sub`; basePlanId is not used. Grace stays 3 days.
- Go-live order (owner decides): service account + Play Console link -> "merge play" -> I merge `play-billing` into `main` -> run `install_play_key.cmd`. Test steps (License tester, Internal testing, audit/log checks) and rollback are in `inbox/WWW.md` (Wynik APP-032).
- 2026-11-27: owner said "merge play"; `play-billing` merged into `main` (6ae77fa), 25 tests pass, deployed. Checked live: `POST /api/shop/play/redeem` answers 503 "not configured" (dry run), `/api/health` 200. Nothing is issued until `PLAY_KEY_FILE` exists: next step is the owner's Google service account + `tools\install_play_key.cmd`.
- APP-033 review (automatic licence codes) is in `inbox/WWW.md`: fixes 1-4 (Reply-To, code e-mail from /api/devices, re-issue on subscription renewal, admin alert on mail failure) wait for the owner's go.

## Admin panel reorganised (2026-11-28)
- `/account/` admin is now tabs: Licences, Requests (new count), Support (open count), Visits, Grant. Licences are folders (chips with counts): All, Web shop, Google Play, Granted, Revoked, No licence; 25 per page + "Show more"; search box matches e-mail, Device ID, phone label, Google Play id (`play-...`), first characters of a Play purchase hash (as in the audit log), order id or licence number (`#12`). Google does not give us the buyer's e-mail or Google account id, so the `play-<id>` is the only Play identity.
- Backend: `GET /api/admin/licences?q=&group=&offset=&limit=` and `POST /api/admin/purge` (removes a REVOKED licence with its phones, or an account with no licence; never an admin or yourself; orders stay; audit line written). `/api/admin/overview` no longer returns users or entitlements. 26 tests pass; checked in a real browser at phone width against a seeded database.


## Legal pages accepted, controller named (2026-11-28)
- Owner accepted the legal pages (Privacy, App privacy, Delete data, Terms) and asked to name the controller **Dariusz Grabowski, United Kingdom** instead of "DG" (About, footer, Terms, Privacy, App privacy, chat knowledge). Supersedes the 2026-10-25 "DG" decision. The 2026-11-28 APP-033 fixes 1-4 are live (Reply-To support@, code mailed from /api/devices, renewal re-issues codes for all phones, admin alert when the receipt mail fails); the PayPal webhook safety net was declined.
