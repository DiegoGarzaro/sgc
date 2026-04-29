#!/bin/sh
set -e
mkdir -p "${MEDIA_ROOT:-/app/media}"
uv run python manage.py migrate --no-input
exec uv run gunicorn app.wsgi:application --bind "0.0.0.0:${PORT:-8080}" --workers 2
