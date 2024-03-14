#!/bin/sh
#
MANAGE_PATH="/transcendence/manage.py"

INSTALLED_APPS="srcs_user srcs_auth srcs_tournament srcs_game srcs_chat srcs_message srcs_core"

makemigrations() {
python $MANAGE_PATH makemigrations $@ --settings=srcs_core.settings
}

makemigrations $INSTALLED_APPS


python $MANAGE_PATH migrate --settings=srcs_core.settings

exec python $MANAGE_PATH runserver --settings=srcs_core.settings 0.0.0.0:8000
