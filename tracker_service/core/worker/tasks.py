from datetime import datetime

from tracker_service.core.worker.config import celery_app
from tracker_service.core.services.notification_service import NotificationService
from tracker_service.core.services.tracker_analysis_service import TrackerAnalysisService
from libs.db import get_db_session_sync


@celery_app.task(bind=True, name="send_weekly_body_tracker_reminder", max_retries=3, default_retry_delay=60)
def send_weekly_body_tracker_reminder(self) -> None:
    """
    Send weekly reminder notification to all active users to update their body measurements.
    This task is scheduled to run once a week.
    """
    try:
        with get_db_session_sync() as db:
            notification_service = NotificationService(db)
            notification_service.create_body_tracker_reminder()
        return f"Weekly body tracker reminder sent at {datetime.now().isoformat()}"
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)


@celery_app.task(bind=True, name="send_daily_tracker_reminder", max_retries=3, default_retry_delay=60)
def send_daily_tracker_reminder(self) -> None:
    """
    Send daily reminder notification to all active users to update their daily activities.
    This task is scheduled to run once a day.
    """
    try:
        with get_db_session_sync() as db:
            notification_service = NotificationService(db)
            notification_service.create_daily_tracker_reminder()
        return f"Daily tracker reminder sent at {datetime.now().isoformat()}"
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)


@celery_app.task(bind=True, name="analyze_body_tracker", max_retries=3, default_retry_delay=60)
def analyze_body_tracker(self, tracker_id: int) -> None:
    """
    Analyze a single body tracker record.
    This task is triggered when a new body tracker record is created.
    """
    try:
        with get_db_session_sync() as db:
            tracker_analysis_service = TrackerAnalysisService(db)
            success = tracker_analysis_service.analyze_body_tracker(tracker_id)

            if success:
                return f"Successfully analyzed body tracker ID {tracker_id}"
            else:
                raise Exception(f"Failed to analyze body tracker ID {tracker_id}")
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)


@celery_app.task(bind=True, name="analyze_daily_tracker", max_retries=3, default_retry_delay=60)
def analyze_daily_tracker(self, tracker_id: int) -> None:
    """
    Analyze a single daily tracker record.
    This task is triggered when a new daily tracker record is created.
    """
    try:
        with get_db_session_sync() as db:
            tracker_analysis_service = TrackerAnalysisService(db)
            success = tracker_analysis_service.analyze_daily_tracker(tracker_id)

            if success:
                return f"Successfully analyzed daily tracker ID {tracker_id}"
            else:
                raise Exception(f"Failed to analyze daily tracker ID {tracker_id}")
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)
