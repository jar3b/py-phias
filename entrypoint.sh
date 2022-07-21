#!/bin/sh
set -e

if [ "$1" = 'python' ]; then
  exec "$@"
else
  python manage.py "$@"
fi
