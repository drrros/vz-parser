#!/bin/sh


python manage.py collectstatic --noinput --clear
rm /code/celerybeat.pid
python manage.py makemigrations --noinput
python manage.py migrate --noinput
exec "$@"
