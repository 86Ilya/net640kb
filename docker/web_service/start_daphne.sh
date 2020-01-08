#!/bin/bash

echo "launching daphne server"
daphne -p 8001 -b 0.0.0.0 -v 2 --access-log /app/logs/daphne_access.log Net640.asgi:application
