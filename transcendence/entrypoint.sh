#!/bin/sh
#
MANAGE_PATH="/transcendence/manage.py"

INSTALLED_APPS="srcs_user srcs_auth srcs_tournament srcs_game srcs_chat srcs_message srcs_core"

makemigrations() {
python $MANAGE_PATH makemigrations $@ --settings=srcs_core.settings
}

makemigrations $INSTALLED_APPS


python $MANAGE_PATH migrate --settings=srcs_core.settings

python $MANAGE_PATH create_superuser --settings=srcs_core.settings

python -m daphne srcs_core.asgi:application -p 8001 -b 0.0.0.0 &

exec gunicorn srcs_core.wsgi --bind 0.0.0.0:8000 --workers 2
