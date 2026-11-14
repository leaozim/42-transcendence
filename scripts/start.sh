#!/usr/bin/env bash
# Starts the application natively (replaces the old Docker entrypoint).
#
# A single Daphne process serves HTTP, WebSockets and static files, so no
# nginx, gunicorn, Redis or PostgreSQL is required. It:
#   1. applies database migrations
#   2. creates the bot superuser (user id 1, required by the chat)
#   3. compiles translations
#   4. runs Daphne on $BIND_ADDRESS:$PORT (default 0.0.0.0:8000)
#
# Settings are read from the environment first, then from <project>/.env.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="$ROOT/transcendence"
ENV_FILE="$ROOT/.env"
VENV="${VENV:-$ROOT/.venv}"

log() { printf '\033[1;34m[start]\033[0m %s\n' "$*"; }
die() { printf '\033[1;31m[start]\033[0m %s\n' "$*" >&2; exit 1; }

if [ -n "${PYTHON:-}" ]; then
    PY="$PYTHON"
elif [ -x "$VENV/bin/python" ]; then
    PY="$VENV/bin/python"
else
    PY="python3"
fi
"$PY" -c 'import django, daphne' 2>/dev/null || die "Django/Daphne not found for $PY. Run 'make setup' (or ./scripts/setup.sh) first."
[ -f "$ENV_FILE" ] || die "Missing $ENV_FILE. Run 'make setup' or copy .env.example to .env and set SECRET_KEY."

# Look up a setting: environment variable > .env file > default.
setting() {
    "$PY" - "$ENV_FILE" "$1" "$2" <<'EOF'
import os, sys
from dotenv import dotenv_values
env_file, name, default = sys.argv[1:4]
print(os.environ.get(name) or dotenv_values(env_file).get(name) or default)
EOF
}

DJANGO_SETTINGS_MODULE="$(setting DJANGO_SETTINGS_MODULE srcs_core.settings)"
export DJANGO_SETTINGS_MODULE
BIND_ADDRESS="$(setting BIND_ADDRESS 0.0.0.0)"
PORT="$(setting PORT 8000)"

cd "$APP_DIR"

log "Applying migrations ($DJANGO_SETTINGS_MODULE)"
"$PY" manage.py migrate --noinput

log "Ensuring bot superuser exists"
"$PY" manage.py create_superuser

log "Compiling translations"
if command -v msgfmt >/dev/null 2>&1; then
    "$PY" manage.py compilemessages
else
    "$PY" "$ROOT/scripts/compile_messages.py" "$APP_DIR/locale"
fi

log "Serving on http://$BIND_ADDRESS:$PORT (HTTP + WebSockets + static files)"
exec "$PY" -m daphne -b "$BIND_ADDRESS" -p "$PORT" srcs_core.asgi:application
