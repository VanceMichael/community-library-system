#!/bin/bash
set -e

echo "Waiting for database to be ready..."
python manage.py wait_for_db 2>/dev/null || sleep 10

echo "Running migrations..."
python manage.py migrate --noinput

echo "Running initialization..."
python manage.py init_library

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec gunicorn library_system.wsgi:application --bind 0.0.0.0:8000 --workers 4
