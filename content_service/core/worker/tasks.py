from content_service.core.worker.config import celery_app
from content_service.core.services.content_shedule import ContentScheduleService
from libs.db import get_db_session_sync


@celery_app.task(bind=True, name="generate_general_blog", max_retries=3, default_retry_delay=60)
def generate_general_blog(self) -> None:
    """
    Task to generate a general blog post
    """
    try:
        with get_db_session_sync() as db:
            content_service = ContentScheduleService(db)
            blog_id = content_service.generate_general_blog()
            if blog_id:
                content_service.publish_blog(blog_id)
        return "Generated and published general blog post"
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)


@celery_app.task(bind=True, name="generate_recipe_blog", max_retries=3, default_retry_delay=60)
def generate_recipe_blog(self) -> None:
    """
    Task to generate a recipe blog post
    """
    try:
        with get_db_session_sync() as db:
            content_service = ContentScheduleService(db)
            blog_id = content_service.generate_recipe_blog()
            if blog_id:
                content_service.publish_blog(blog_id)
        return "Generated and published recipe blog post"
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)
