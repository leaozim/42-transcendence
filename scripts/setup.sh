#!/usr/bin/env bash
# Installs everything needed to run the project natively (no Docker):
#   - a Python virtualenv in .venv with the project requirements
#   - a .env file (copied from .env.example) with a freshly generated SECRET_KEY
#
# Environment overrides:
#   PYTHON=/path/to/python   interpreter to use (default: first of python3.12/3.11/3.10/python3)
#   VENV=/path/to/venv        virtualenv location (default: <project>/.venv)
#   USE_VENV=0                install into the current Python environment instead
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${VENV:-$ROOT/.venv}"
USE_VENV="${USE_VENV:-1}"
REQUIREMENTS="$ROOT/transcendence/requirements/local.txt"

log() { printf '\033[1;34m[setup]\033[0m %s\n' "$*"; }
die() { printf '\033[1;31m[setup]\033[0m %s\n' "$*" >&2; exit 1; }

# The pinned requirements (Django 4.2, pillow 10.2, cffi 1.16, ...) ship
# prebuilt wheels for CPython 3.10 - 3.12 only.
is_supported_python() {
    "$1" -c 'import sys; sys.exit(0 if (3, 10) <= sys.version_info[:2] <= (3, 12) else 1)' 2>/dev/null
}

find_python() {
    if [ -n "${PYTHON:-}" ]; then
        command -v "$PYTHON" >/dev/null 2>&1 || die "PYTHON=$PYTHON not found"
        if ! is_supported_python "$PYTHON"; then
            log "WARNING: $PYTHON is not Python 3.10-3.12; installing the pinned requirements may fail."
        fi
        echo "$PYTHON"
        return
    fi
    for candidate in python3.12 python3.11 python3.10 python3; do
        if command -v "$candidate" >/dev/null 2>&1 && is_supported_python "$candidate"; then
            echo "$candidate"
            return
        fi
    done
    die "Python 3.10, 3.11 or 3.12 is required. Install one, or point PYTHON=/path/to/python at it."
}

if [ "$USE_VENV" = "1" ]; then
    if [ -x "$VENV/bin/python" ]; then
        log "Using existing virtualenv at $VENV"
    else
        PY="$(find_python)"
        log "Creating virtualenv at $VENV with $("$PY" --version 2>&1)"
        "$PY" -m venv "$VENV" || die "Could not create a virtualenv. On Debian/Ubuntu install the 'python3-venv' package, or re-run with USE_VENV=0 to install into the current environment."
    fi
    PY="$VENV/bin/python"
else
    PY="$(find_python)"
    log "USE_VENV=0: installing into $("$PY" -c 'import sys; print(sys.prefix)')"
fi

log "Installing Python requirements"
"$PY" -m pip install --upgrade pip >/dev/null
"$PY" -m pip install -r "$REQUIREMENTS"

if [ -f "$ROOT/.env" ]; then
    log ".env already exists, leaving it untouched"
else
    log "Creating .env from .env.example (with a generated SECRET_KEY)"
    SECRET_KEY="$("$PY" -c 'import secrets; print(secrets.token_urlsafe(50))')"
    sed "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" "$ROOT/.env.example" > "$ROOT/.env"
fi

if ! command -v msgfmt >/dev/null 2>&1; then
    log "Note: GNU gettext (msgfmt) not found; translations will be compiled with the bundled Python fallback."
fi

log "Done. Start the server with: make run   (or ./scripts/start.sh)"
