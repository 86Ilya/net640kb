#!/bin/bash

if [[ "$DEPLOY_ENV" -eq "DEVELOP" ]]
then
  python /app/manage.py makemigrations
fi
python /app/manage.py migrate
python /app/manage.py collectstatic --noinput
echo "launching uwsgi"
uwsgi --ini /app/docker/web_service/uwsgi.ini
