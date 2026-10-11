# ServMod website – project index (read this first)

Last updated: 2026-10-11 (site commit cf7ed02). Keep this file current: when something is added/changed/learned, update it in the same commit.
Mirror on the PC: `C:\Users\grabo\Desktop\Arduino\ServMod\handoff\website\` (copy of `docs/`). Master copy = this repo.

## What it is
Static marketing site + small FastAPI backend for **ServMod** (Android toolbox for maintenance engineers), live at https://servmod.com. Site and app GUI are **English only**; the owner (Dariusz) talks Polish.

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
Admin (ADMIN_EMAILS only): `/api/admin/overview|grant|revoke|ticket`.
All POST/DELETE need header `X-Requested-With: servmod` and same-origin. SQLite tables: users, login_tokens, sessions, entitlements, licences, tickets, rate, audit.

## Infrastructure
- Domain servmod.com on Cloudflare DNS -> Hetzner server (167.233.108.235; the box formerly ran the trading bots – bot files still there, do not delete without asking). nginx + certbot TLS.
- Server paths: site `/var/www/servmod/`, **update feed** `/var/www/servmod/servmod/` (never touched by sync), backend `/opt/servmod-app`, data `/var/lib/servmod` (SQLite), licence signing key `/etc/servmod/license_private.key`, repo checkout `/var/lib/servmod-repo`, sync log `/var/log/servmod-sync.log`.
- Mail: Resend (MAIL_MODE=resend, key in server env, never in repo); inbound support@servmod.com via Cloudflare Email Routing (delivery confirmed 2026-10-11).
- Update feed: `/servmod/version.json`, `/servmod/beta/version.json`, `/servmod/history.json`, `/servmod/releases/*.apk`. **APK downloads are locked in nginx until Dariusz says "unlock".**

## Current status / open items
- Done: full static site, manuals search, account login, support form (works), licence activation codes, visible Sign-in button.
- Not done: shop/cart/payments (Stripe + PayPal, reuse engine from qubivibe.com – waiting for Dariusz to show those files), automatic licence e-mail after purchase, publishing the APK (only on "unlock").
- Known gotcha: do not reuse DOM id `acct` (account page uses it) – header link is `acct-link`.
