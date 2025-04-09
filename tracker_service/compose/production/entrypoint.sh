#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

export CELERY_FIT_QUEUE_NAME=${FIT_QUEUE_NAME}
export CELERY_FIT_WORKER_NAME=${FIT_WORKER_NAME}

celery -A tracker_service.core.worker.tasks.celery_app worker --loglevel=ERROR -E --queues=${CELERY_FIT_QUEUE_NAME} -n ${CELERY_FIT_WORKER_NAME}@%n
