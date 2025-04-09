from content_service.core.worker.config import celery_app


@celery_app.task(bind=True, name="example", max_retries=3, default_retry_delay=60)
def example_task(self) -> None:
    return "Example task completed"
