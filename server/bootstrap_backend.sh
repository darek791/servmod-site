#!/bin/bash
# One-time server setup for the ServMod API. Reads settings from the environment (set by install_backend.ps1).
set -eu
export DEBIAN_FRONTEND=noninteractive
command -v python3 >/dev/null && python3 -m venv --help >/dev/null 2>&1 || apt-get install -y -q python3-venv python3-pip
command -v rsync >/dev/null || apt-get install -y -q rsync
id servmod >/dev/null 2>&1 || useradd --system --home /var/lib/servmod --shell /usr/sbin/nologin servmod
mkdir -p /opt/servmod-app /var/lib/servmod /etc/servmod
chown servmod:servmod /var/lib/servmod; chmod 700 /var/lib/servmod
[ -x /opt/servmod-app/venv/bin/pip ] || python3 -m venv /opt/servmod-app/venv
umask 077
if [ -z "${RESEND_API_KEY:-}" ] && [ -f /etc/servmod/api.env ]; then
  OLDKEY=$(grep '^RESEND_API_KEY=' /etc/servmod/api.env | cut -d= -f2-)
  if [ -n "$OLDKEY" ]; then RESEND_API_KEY="$OLDKEY"; MAIL_MODE=resend; fi
fi
cat > /etc/servmod/api.env <<ENV
SITE_URL=https://servmod.com
ADMIN_EMAILS=${ADMIN_EMAILS}
MAIL_MODE=${MAIL_MODE}
MAIL_FROM=${MAIL_FROM}
RESEND_API_KEY=${RESEND_API_KEY:-}
SERVMOD_DATA=/var/lib/servmod
LICENSE_KEY=/etc/servmod/license_private.key
ENV
chown root:servmod /etc/servmod/api.env; chmod 640 /etc/servmod/api.env
[ -f /etc/servmod/license_private.key ] && chown root:servmod /etc/servmod/license_private.key && chmod 640 /etc/servmod/license_private.key
install -m 755 /tmp/servmod-sync.sh /usr/local/bin/servmod-sync
touch /var/log/servmod-sync.log
systemctl enable servmod-api >/dev/null 2>&1 || true
rm -f /var/lib/servmod-sync.head /var/lib/servmod-sync.req
/usr/local/bin/servmod-sync
sleep 3
systemctl is-active servmod-api && curl -fsS http://127.0.0.1:8100/api/health && echo
tail -5 /var/log/servmod-sync.log
