#!/bin/sh
# Get container ID
container_id="$(docker ps | grep addon.*tydom2mqtt* | awk '{print $1}')"
# Fix restart policy
docker update --restart=always $container_id