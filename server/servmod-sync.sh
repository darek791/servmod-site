#!/bin/bash
# servmod-sync v2: pulls GitHub main, deploys site/, nginx conf and (if installed) the API backend.
set -u
umask 022
REPO_URL="https://github.com/darek791/servmod-site.git"
REPO=/var/lib/servmod-repo
LOCK=/run/servmod-sync.lock
exec 9>"$LOCK"; flock -n 9 || exit 0
log(){ echo "$(date -u +%FT%TZ) $*" >> /var/log/servmod-sync.log; }
if [ ! -d "$REPO/.git" ]; then git clone -q --depth 1 "$REPO_URL" "$REPO" || { log "clone failed"; exit 1; }; fi
cd "$REPO" || exit 1
git fetch -q origin main || { log "fetch failed"; exit 1; }
NEW=$(git rev-parse origin/main); OLD=$(cat /var/lib/servmod-sync.head 2>/dev/null || true)
[ "$NEW" = "$OLD" ] && exit 0
git reset -q --hard origin/main
[ -f site/index.html ] || { log "abort: site/index.html missing at $NEW"; exit 1; }
rsync -a --delete --exclude 'servmod/' site/ /var/www/servmod/ && chown -R www-data:www-data /var/www/servmod
# nginx
if [ -f nginx/servmod.conf ] && ! cmp -s nginx/servmod.conf /etc/nginx/sites-available/servmod; then
  cp /etc/nginx/sites-available/servmod /etc/nginx/sites-available/servmod.prev 2>/dev/null
  cp nginx/servmod.conf /etc/nginx/sites-available/servmod
  if nginx -t >/dev/null 2>&1; then systemctl reload nginx; log "nginx conf applied"; else cp /etc/nginx/sites-available/servmod.prev /etc/nginx/sites-available/servmod; log "nginx conf REJECTED, kept previous"; fi
fi
# backend (only after install_backend has created the venv)
if [ -x /opt/servmod-app/venv/bin/pip ] && [ -d backend/servmod_api ]; then
  H=$(cat backend/requirements.txt | sha256sum | cut -c1-16)
  rsync -a --delete --exclude '__pycache__' backend/servmod_api/ /opt/servmod-app/servmod_api/
  if [ "$H" != "$(cat /var/lib/servmod-sync.req 2>/dev/null)" ]; then
    /opt/servmod-app/venv/bin/pip install -q -r backend/requirements.txt && echo "$H" > /var/lib/servmod-sync.req || log "pip install failed"
  fi
  cmp -s server/servmod-api.service /etc/systemd/system/servmod-api.service || { cp server/servmod-api.service /etc/systemd/system/servmod-api.service; systemctl daemon-reload; }
  chown -R root:servmod /opt/servmod-app/servmod_api; chmod -R u=rwX,g=rX,o= /opt/servmod-app/servmod_api
  systemctl restart servmod-api && log "api restarted"
fi
cmp -s server/servmod-sync.sh /usr/local/bin/servmod-sync || install -m 755 server/servmod-sync.sh /usr/local/bin/servmod-sync
echo "$NEW" > /var/lib/servmod-sync.head
log "deployed $NEW"
