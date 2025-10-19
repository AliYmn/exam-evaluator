from celery import Celery

from libs import settings

# Use Redis as broker if RabbitMQ not configured (for Fly.io deployment)
if hasattr(settings, "RABBITMQ_HOST") and settings.RABBITMQ_HOST:
    broker_url = (
        f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//"
    )
else:
    # Fallback to Redis broker (simpler for deployment)
    redis_password = f":{settings.REDIS_PASSWORD}@" if settings.REDIS_PASSWORD else ""
    broker_url = f"redis://{redis_password}{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"

# Configure backend URL - prioritize DATABASE_URL if available (for Fly.io managed Postgres)
if settings.DATABASE_URL:
    # Use DATABASE_URL if provided
    base_url = settings.DATABASE_URL.replace("postgres://", "postgresql://")
    # Remove sslmode query parameter if present (Celery backend doesn't need it)
    if "?" in base_url:
        base_url = base_url.split("?")[0]
    backend_url = f"db+{base_url}"
else:
    # Build from individual variables
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
