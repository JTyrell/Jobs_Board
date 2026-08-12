#!/bin/bash
set -e

cd SonaJobs
python manage.py migrate
exec gunicorn jobs_platform.wsgi:application --bind 0.0.0.0:$PORT
