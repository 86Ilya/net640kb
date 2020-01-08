#!/usr/bin/env bash

function finish() {
        echo "Exiting"
	docker-compose -f docker-compose-develop.yml down
}

trap finish SIGINT

docker-compose -f docker-compose-develop.yml build
docker-compose -f docker-compose-develop.yml up
