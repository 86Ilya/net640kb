#!/usr/bin/env bash

docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up -d db
docker-compose -f docker-compose.yml up -d redis 
docker-compose -f docker-compose-develop.yml up -d user_cache
docker-compose -f docker-compose.yml up -d web
# TODO
sleep 5
docker-compose -f docker-compose.yml up nginx 
docker-compose -f docker-compose.yml stop db
docker-compose -f docker-compose.yml stop redis 
docker-compose -f docker-compose.yml stop web
