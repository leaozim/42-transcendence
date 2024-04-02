#!/bin/sh
#

set -xo

MANAGE_PATH="/transcendence/manage.py"


if [[ $DEV ]]; then
  SETTINGS="srcs_core.settings"
else
  SETTINGS="srcs_core.settings_prod"
fi

INSTALLED_APPS="srcs_user srcs_auth srcs_tournament srcs_game srcs_chat srcs_message srcs_core"

makemigrations() {
python $MANAGE_PATH makemigrations $@ --settings=$SETTINGS
}

makemigrations $INSTALLED_APPS


python $MANAGE_PATH migrate --settings=$SETTINGS

python $MANAGE_PATH create_superuser --settings=$SETTINGS

python $MANAGE_PATH compilemessages --settings=$SETTINGS

python -m daphne srcs_core.asgi:application -p 8001 -b 0.0.0.0 &

exec gunicorn srcs_core.wsgi --bind 0.0.0.0:8000 --workers 4
