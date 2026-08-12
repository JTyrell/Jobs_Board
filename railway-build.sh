#!/bin/bash
set -e

cd SonaJobs
python -m pip install -r requirements.txt
python manage.py makemigrations accounts jobs
python manage.py collectstatic --noinput
