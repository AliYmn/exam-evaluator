from datetime import datetime

from tracker_service.core.worker.config import celery_app
from tracker_service.core.services.notification_service import NotificationService
from libs.db import get_db_session_sync


@celery_app.task(bind=True, name="send_weekly_body_tracker_reminder", max_retries=3, default_retry_delay=60)
def send_weekly_body_tracker_reminder(self) -> None:
    """
    Send weekly reminder notification to all active users to update their body measurements.
    This task is scheduled to run once a week.
    """
    with get_db_session_sync() as db:
        notification_service = NotificationService(db)
        notification_service.create_body_tracker_reminder()
    return f"Weekly body tracker reminder sent at {datetime.now().isoformat()}"


@celery_app.task(bind=True, name="send_daily_tracker_reminder", max_retries=3, default_retry_delay=60)
def send_daily_tracker_reminder(self) -> None:
    """
    Send daily reminder notification to all active users to update their daily activities.
    This task is scheduled to run once a day.
    """
    with get_db_session_sync() as db:
        notification_service = NotificationService(db)
        notification_service.create_daily_tracker_reminder()
    return f"Daily tracker reminder sent at {datetime.now().isoformat()}"
