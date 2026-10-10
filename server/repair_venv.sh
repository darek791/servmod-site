#!/bin/bash
# Rebuilds the API virtualenv once per marker version (runs as root from the unit's ExecStartPre).
M=/var/lib/servmod-venv-v3
[ -f "$M" ] && exit 0
exec 9>/run/servmod-venv.lock; flock 9
[ -f "$M" ] && exit 0
rm -rf /opt/servmod-app/venv
python3 -m venv /opt/servmod-app/venv || exit 1
/opt/servmod-app/venv/bin/pip install -q -r /var/lib/servmod-repo/backend/requirements.txt || exit 1
/opt/servmod-app/venv/bin/python -c "from fastapi import FastAPI; import uvicorn, click" || exit 1
touch "$M"
