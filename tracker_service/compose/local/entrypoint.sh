#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

export CELERY_TRACKER_QUEUE_NAME=${TRACKER_QUEUE_NAME}
export CELERY_TRACKER_WORKER_NAME=${TRACKER_WORKER_NAME}

# Use INFO log level for local development to see more details
celery -A tracker_service.core.worker.tasks.celery_app worker --loglevel=INFO -E --queues=${CELERY_TRACKER_QUEUE_NAME} -n ${CELERY_TRACKER_WORKER_NAME}@%n
