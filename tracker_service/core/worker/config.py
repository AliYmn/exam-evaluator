from celery import Celery
from celery.schedules import crontab

from libs import settings

broker_url = (
    f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//"
)
backend_url = f"db+postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"

celery_app = Celery(
    settings.TRACKER_WORKER_NAME,
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
        "analyze_body_tracker": {"queue": settings.TRACKER_QUEUE_NAME},
        "analyze_daily_tracker": {"queue": settings.TRACKER_QUEUE_NAME},
    },
    timezone="UTC",
    beat_schedule={
        # Send weekly body tracker reminder every Monday at 9:00 AM
        "send-weekly-body-tracker-reminder": {
            "task": "send_weekly_body_tracker_reminder",
            "schedule": crontab(day_of_week=1, hour=9, minute=0),
        },
        # Send daily tracker reminder every day at 8:00 AM
        "send-daily-tracker-reminder": {
            "task": "send_daily_tracker_reminder",
            "schedule": crontab(hour=8, minute=0),
        },
    },
)
