from celery import Celery

from libs import settings

broker_url = (
    f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//"
)
backend_url = f"db+postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"

celery_app = Celery(
    settings.CONTENT_WORKER_NAME,
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
        "process_answer_key": {"queue": "content_queue"},
        "process_student_answer": {"queue": "content_queue"},
        "evaluate_student_responses": {"queue": "content_queue"},
    },
    timezone="UTC",
)
