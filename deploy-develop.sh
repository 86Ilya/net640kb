#!/usr/bin/env bash

function finish() {
        echo "Exiting"
	docker-compose -f docker-compose-develop.yml down
}

trap finish SIGINT

docker-compose -f docker-compose-develop.yml build
docker-compose -f docker-compose-develop.yml up -d db
docker-compose -f docker-compose-develop.yml up -d redis
docker-compose -f docker-compose-develop.yml up -d user_cache
docker-compose -f docker-compose-develop.yml up -d web
docker-compose -f docker-compose-develop.yml up -d selenium
sleep 5
docker-compose -f docker-compose-develop.yml up nginx
