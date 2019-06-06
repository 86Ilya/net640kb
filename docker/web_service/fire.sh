#!/bin/bash

python /app/manage.py migrate 
python /app/manage.py collectstatic --noinput
echo "launching uwsgi"
uwsgi --ini /app/docker/web_service/uwsgi.ini --check-static /app/static
echo "launching daphne server"
daphne -p 8001 -b 0.0.0.0 --access-log /app/logs/daphne_access.log Net640.asgi:application
