#!/bin/sh
#

set -xo

MANAGE_PATH="/transcendence/manage.py"


SETTINGS="srcs_core.settings"

INSTALLED_APPS="srcs_user srcs_auth srcs_tournament srcs_game srcs_chat srcs_message srcs_core"

makemigrations() {
python $MANAGE_PATH makemigrations $@ --settings=$SETTINGS
}

makemigrations $INSTALLED_APPS


python $MANAGE_PATH migrate --settings=$SETTINGS

python $MANAGE_PATH create_superuser --settings=$SETTINGS

python $MANAGE_PATH compilemessages --settings=$SETTINGS

exec gunicorn srcs_core.wsgi --access-logfile '-' --error-logfile '-' --bind 0.0.0.0:8000 --workers 4
