from celery import Celery
from celery.schedules import crontab

from libs import settings

broker_url = (
    f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//"
)
backend_url = f"db+postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"

celery_app = Celery(
    settings.FIT_WORKER_NAME,
    broker=broker_url,
    backend=backend_url,
)

celery_app.conf.update(
    task_acks_late=settings.DEBUG == False,
    broker_connection_retry_on_startup=True,
    task_ignore_result=False,
    result_extended=True,
    result_serializer="json",
    task_serializer="json",
    accept_content=["json"],
    task_routes={
        "check_all_fasting_plans": {"queue": settings.FIT_QUEUE_NAME},
        "check_user_fasting_plans": {"queue": settings.FIT_QUEUE_NAME},
    },
    timezone="UTC",
)


celery_app.conf.beat_schedule = {
    "check_all_fasting_plans": {
        "task": "check_all_fasting_plans",
        "schedule": crontab(minute="*/5"),
    },
}
