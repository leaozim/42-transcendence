#!/bin/sh
#
MANAGE_PATH="/transcendence/manage.py"

python $MANAGE_PATH migrate --settings=srcs_core.settings

exec python $MANAGE_PATH runserver --settings=srcs_core.settings 0.0.0.0:8000
