from datetime import datetime

from fit_service.core.worker.config import celery_app
from fit_service.core.services.schedule_fasting import ScheduleFastingService
from libs.db import get_db_session_sync


@celery_app.task(bind=True, name="example", max_retries=3, default_retry_delay=60)
def example_task(self) -> None:
    return "Example task completed"


@celery_app.task(bind=True, name="check_fasting_plans", max_retries=3, default_retry_delay=60)
def check_fasting_plans(self) -> str:
    """
    Check all active fasting plans and create new sessions if needed.
    This task checks if any fasting plan has reached its finish date and creates
    a new session if needed, marking the previous session as completed.
    """
    with get_db_session_sync() as db:
        schedule_service = ScheduleFastingService(db)
        completed_plans, new_sessions = schedule_service.check_and_update_fasting_plans()

    return f"Checked fasting plans at {datetime.now().isoformat()}: Completed {completed_plans} plans, Created {new_sessions} new sessions"
