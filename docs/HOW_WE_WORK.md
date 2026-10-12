# How we work on ServMod (workflow, deploy, PC, GitHub)

## People and language
Dariusz writes Polish, usually from a phone. Claude answers in Polish; **website and app GUI text is English only**. Keep replies short: what was done, what to check, next step.

## Where Claude works
1. **Website** – in the cloud container clone `/home/claude/servmod-site` (remote `origin` = github.com/darek791/servmod-site, push works from there). Flow: edit `src/*` or `backend/*` -> `cd src && python3 build.py` (regenerates `site/`) -> `git add -A && git commit` -> `git push`. Server pulls `main` every minute (`servmod-sync`): rsyncs `site/`, applies nginx conf if valid, syncs backend and restarts `servmod-api`. Live in ~60 s. Check: `curl -s https://servmod.com/...` or `git ls-remote origin main` = HEAD.
2. **Android app** – on the user's PC through the device bridge: source `C:\Users\grabo\Desktop\Arduino\wl200_android`, shared folder `...\Arduino\ServMod` (releases\, handoff\, web\ = old local site copy, do not use as master). Edit with `device_bash` (python/sed in `$HOME/mnt/Arduino/...`), build in Android Studio by computer use (see `handoff/03_BUILD_RELEASE_HOWTO.md`: open app -> Build menu -> Assemble; wait <=50 s per call; read result by zoom on Build panel), copy APK to `ServMod\releases\ServMod-<ver>-<tag>.apk`, bump versionCode/versionName each delivery, stage and **send APK in chat** (SendUserFile, <=30 MiB).
3. **Server (Hetzner)** – no ssh from the bridge. Changes go through the repo (auto-sync). One-off server actions are done by `.cmd` scripts that Dariusz double-clicks on the PC (`tools/install_backend.cmd`, `tools/release.py`).

## Rules
1. Work autonomously; ask only when a decision is irreversible or truly ambiguous.
2. Secrets (API keys, passwords, Resend key) only typed by Dariusz in PC prompts, never in chat or repo. Never commit keys, .env, APKs, `license_private.key`, `servmod-release.jks`. These two key files never leave the PC.
3. Downloads stay locked until he writes "unlock". Publishing a release only on his command (`tools/release.py` from the PC).
4. Scripts for him = double-click `.cmd` files, not pasted commands.
5. Don't delete the old trading-bot files on the server without asking.
6. Prefer the repo as source of truth: every change committed with a clear message, ending with the attribution lines required by the session.
7. After each stage: update `docs/INDEX.md` (and this file if the process changed), copy `docs/` to the PC (`ServMod\handoff\website\`) and mirror to the Claude Project docs (`claude/servmod-website-index.md`).

## Session start checklist (any new Claude session)
1. Read project docs: `claude/servmod-handoff.md`, `claude/servmod-status-*.md`, `claude/servmod-backlog.md`, `claude/servmod-website-index.md`.
2. Website work: `git pull` in `/home/claude/servmod-site` (clone from GitHub if missing), read `docs/INDEX.md`.
3. App work: read `ServMod\handoff\00_START_HERE.md` on the PC.

## Testing / checks
- Backend tests: `cd backend && python3 -m pytest tests -q` (10 tests incl. waiting list).
- Site: after build, grep generated pages for the change; check mobile width (nav collapses under 780 px).
- Mail: support form message must be >=10 chars; delivery path form -> Resend -> support@servmod.com (Cloudflare Email Routing).
