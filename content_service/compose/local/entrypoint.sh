#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

export CELERY_CONTENT_QUEUE_NAME=${CONTENT_QUEUE_NAME}
export CELERY_CONTENT_WORKER_NAME=${CONTENT_WORKER_NAME}

# Use INFO log level for local development to see more detFITls
celery -A fit_service.core.worker.tasks.celery_app worker --loglevel=INFO -E --queues=${CELERY_CONTENT_QUEUE_NAME} -n ${CELERY_CONTENT_WORKER_NAME}@%n
