#!/bin/bash

scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r ./docker-compose.yml $WEB_SERVER_SSH_HOST:$COMPOSE_FILE_DIR/$COMPOSE_FILE_NAME

ssh $WEB_SERVER_SSH_HOST << EOF
    docker login ghcr.io -u $REGISTRY_USERNAME -p $REGISTRY_PASSWORD
    docker system prune -af
    docker compose -f $COMPOSE_FILE_DIR/$COMPOSE_FILE_NAME pull
    docker compose -f $COMPOSE_FILE_DIR/$COMPOSE_FILE_NAME up -d
EOF
sleep 30