#!/bin/sh
set -e
mkdir -p "${MEDIA_ROOT:-/app/media}"
python manage.py migrate --no-input
exec gunicorn app.wsgi:application \
    --bind "0.0.0.0:${PORT:-8080}" \
    --workers 2 \
    --preload \
    --timeout 300 \
    --access-logfile -
