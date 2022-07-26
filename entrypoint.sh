#!/bin/sh
set -e

case "$1" in
python) exec "$@" ;;
/*) exec "$@" ;;
*) python manage.py "$@" ;;
esac
