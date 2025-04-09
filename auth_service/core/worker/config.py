from celery import Celery

from libs import settings

broker_url = (
    f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//"
)
backend_url = f"db+postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"

celery_app = Celery(
    settings.AUTH_WORKER_NAME,
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
        "send_email": {"queue": settings.AUTH_QUEUE_NAME},
        "send_template_email": {"queue": settings.AUTH_QUEUE_NAME},
        "send_welcome_email": {"queue": settings.AUTH_QUEUE_NAME},
        "send_password_reset_email": {"queue": settings.AUTH_QUEUE_NAME},
        "send_password_changed_email": {"queue": settings.AUTH_QUEUE_NAME},
        "send_bulk_emails": {"queue": settings.AUTH_QUEUE_NAME},
    },
    timezone="UTC",
)
