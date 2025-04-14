from content_service.core.worker.config import celery_app
from content_service.core.services.content_shedule import ContentScheduleService
from libs.db import get_db_session_sync


DEST_LANGUAGES = ["en", "tr"]


@celery_app.task(bind=True, name="generate_general_blog", max_retries=3, default_retry_delay=60)
def generate_general_blog(self) -> None:
    try:
        with get_db_session_sync() as db:
            content_service = ContentScheduleService(db)
            for lang in DEST_LANGUAGES:
                blog_id = content_service.generate_general_blog(language=lang)
                if blog_id:
                    content_service.publish_blog(blog_id)
        return "Generated and published general blog post(s) for all languages"
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)


@celery_app.task(bind=True, name="generate_recipe_blog", max_retries=3, default_retry_delay=60)
def generate_recipe_blog(self) -> None:
    try:
        with get_db_session_sync() as db:
            content_service = ContentScheduleService(db)
            for lang in DEST_LANGUAGES:
                blog_id = content_service.generate_recipe_blog(language=lang)
                if blog_id:
                    content_service.publish_blog(blog_id)
        return "Generated and published recipe blog post(s) for all languages"
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)
