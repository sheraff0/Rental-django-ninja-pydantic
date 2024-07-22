#!/bin/bash

set -o errexit
set -o nounset

export TZ='Europe/Moscow'

celery \
    --app=config.celery \
    --broker="${REDIS_URL}" \
flower \
    --basic_auth="${CELERY_FLOWER_USER}:${CELERY_FLOWER_PASSWORD}"
