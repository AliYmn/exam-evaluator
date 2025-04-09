#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

export CELERY_AUTH_QUEUE_NAME=${AUTH_QUEUE_NAME}
export CELERY_AUTH_WORKER_NAME=${AUTH_WORKER_NAME}

celery -A auth_service.core.worker.tasks.celery_app worker --loglevel=ERROR -E --queues=${CELERY_AUTH_QUEUE_NAME} -n ${CELERY_AUTH_WORKER_NAME}@%n
