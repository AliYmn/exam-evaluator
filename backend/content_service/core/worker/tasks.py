from content_service.core.worker.config import celery_app


@celery_app.task(name="process_answer_key")
def process_answer_key_task(evaluation_id: str, answer_key_bytes: bytes):
    pass
