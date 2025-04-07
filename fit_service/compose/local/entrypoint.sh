#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

export CELERY_FIT_QUEUE_NAME=${FIT_QUEUE_NAME}
export CELERY_FIT_WORKER_NAME=${FIT_WORKER_NAME}

# Use INFO log level for local development to see more detFITls
celery -A fit_service.core.worker.tasks.celery_app worker --loglevel=INFO -E --queues=${CELERY_FIT_QUEUE_NAME} -n ${CELERY_FIT_WORKER_NAME}@%n
