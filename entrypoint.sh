#!/bin/sh


python manage.py collectstatic --noinput --clear
rm /code/celerybeat.pid
python manage.py makemigrations --noinput
python manage.py migrate --noinput
# start celery worker
#celery --app=vz_parser_frontend worker --loglevel=DEBUG &
# start celery beat
#celery --app=vz_parser_frontend beat --loglevel=DEBUG &
exec "$@"
