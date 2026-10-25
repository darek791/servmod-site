# ServMod website – project index (read this first)

Last updated: 2026-10-15. Keep this file current: when something is added/changed/learned, update it in the same commit.
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
`/` home · `/features.html` modules · `/equipment.html` · `/guides.html` connection guides · `/manuals/` fault codes · `/pricing.html` (no shop yet) · `/support.html` (form -> `/api/support`) · `/account/` (login by e-mail link/6-digit code, no passwords) · `/waitlist.html` (waiting list: join form, confirm/unsubscribe landing via `#confirm=`/`#unsub=` fragment), `/licence.html`, `/privacy.html`, `/terms.html`, `/refunds.html` · `404.html`. Header has an always-visible **Sign in / My account** button (`#acct-link`).

## Backend API (`/api/*`, proxied by nginx to 127.0.0.1:8100)
Public: `GET /api/health`, `GET /api/latest.apk` (302 to newest APK in feed; 404 while none published), `POST /api/support` (valid e-mail, message 10-5000 chars, rate-limited, stored as ticket + mailed to SUPPORT_TO or first ADMIN_EMAIL).
Auth: `POST /api/auth/request|verify|logout`. Account: `GET /api/me`, `POST /api/devices` (Device ID -> activation code), `POST /api/devices/release`, `GET /api/me/export`, `DELETE /api/me`.
Waiting list: `POST /api/waitlist` (double opt-in: sends confirm mail), `POST /api/waitlist/confirm|unsubscribe` ({token}), `POST /api/waitlist/me` ({on}, signed in; also a checkbox on the account page). Admin (ADMIN_EMAILS only): `/api/admin/overview|grant|revoke|ticket`, `POST /api/admin/waitlist/notify` ({subject,text,test:true} sends only to the admin; a real send needs `confirm:true`, goes to confirmed rows not yet notified unless `again:true`, in a background thread 0.6 s apart). Admin UI is the Waiting list block on the account page.
All POST/DELETE need header `X-Requested-With: servmod` and same-origin. SQLite tables: waitlist (email, confirmed, tok, source, notified), users, login_tokens, sessions, entitlements, licences, tickets, rate, audit.

## Infrastructure
- Domain servmod.com on Cloudflare DNS -> Hetzner server (167.233.108.235; the box formerly ran the trading bots – bot files still there, do not delete without asking). nginx + certbot TLS.
- Server paths: site `/var/www/servmod/`, **update feed** `/var/www/servmod/servmod/` (never touched by sync), backend `/opt/servmod-app`, data `/var/lib/servmod` (SQLite), licence signing key `/etc/servmod/license_private.key`, repo checkout `/var/lib/servmod-repo`, sync log `/var/log/servmod-sync.log`.
- Mail: Resend (MAIL_MODE=resend, key in server env, never in repo); inbound support@servmod.com via Cloudflare Email Routing (delivery confirmed 2026-10-11).
- Update feed: `/servmod/version.json`, `/servmod/beta/version.json`, `/servmod/history.json`, `/servmod/releases/*.apk`. **APK downloads are locked in nginx until the owner says "unlock".**

## Current status / open items
- 2026-10-15 content refresh to app 0.55: `APP_VERSION` 0.55, `MODULES` list now 17 tools (added Tools, USB Tools, NFC & Barcode, Zodiac Printers, ServMod Box, Steppers, My Stuff; Danfoss FC 280 in Inverters; Printers cable check), features/equipment/guides updated (Hitachi: WL200 USB ok, WJ200 via RS-485 only). When the app gets new modules, edit `MODULES`, the `features()` cards and `equipment()`/`guides()` in src/build.py.
- Done: full static site, manuals search, account login, support form (works), licence activation codes, visible Sign-in button.
- Waiting list built 2026-10-12: send the release e-mail from the account page (admin) when the first public version is published, together with the "unlock".
- Not done: shop/cart/payments (Stripe + PayPal, reuse engine from qubivibe.com – waiting for the owner to show those files), automatic licence e-mail after purchase, publishing the APK (only on "unlock").
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
