from fit_service.core.worker.config import celery_app
from fit_service.core.services.fasting_schedule import FastingScheduleService
from fit_service.core.services.fasting_analysis_service import FastingAnalysisService
from libs.db import get_db_session_sync


@celery_app.task(bind=True, name="check_all_fasting_plans", max_retries=3, default_retry_delay=60)
def check_all_fasting_plans(self) -> None:
    """
    Main task that gets all users with active fasting plans and creates individual tasks for each user
    """
    try:
        with get_db_session_sync() as db:
            fasting_service = FastingScheduleService(db)
            user_ids = fasting_service.get_users_with_active_plans()
            # Create individual tasks for each user
            for user_id in user_ids:
                check_user_fasting_plans.apply_async(args=(user_id,))
        return f"Created fasting plan check tasks for {len(user_ids)} users"
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)


@celery_app.task(bind=True, name="check_user_fasting_plans", max_retries=3, default_retry_delay=60)
def check_user_fasting_plans(self, user_id: int) -> None:
    """
    Task to check and update fasting plans for a specific user
    """
    try:
        with get_db_session_sync() as db:
            fasting_service = FastingScheduleService(db)
            updated_plans = fasting_service.check_user_fasting_plans(user_id)
        return f"Updated {updated_plans} fasting plans for user {user_id}"
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)


@celery_app.task(bind=True, name="analyze_fasting_workout_log", max_retries=3, default_retry_delay=60)
def analyze_fasting_workout_log(self, log_id: int, language: str) -> None:
    """
    Analyze a single fasting workout log.
    This task is triggered when a new workout log is created.
    """
    try:
        with get_db_session_sync() as db:
            analysis_service = FastingAnalysisService(db)
            success = analysis_service.analyze_workout_log(log_id, language)

            if success:
                return f"Successfully analyzed fasting workout log ID {log_id}"
            else:
                raise Exception(f"Failed to analyze fasting workout log ID {log_id}")
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)


@celery_app.task(bind=True, name="analyze_fasting_meal_log", max_retries=3, default_retry_delay=60)
def analyze_fasting_meal_log(self, log_id: int, language: str) -> None:
    """
    Analyze a single fasting meal log.
    This task is triggered when a new meal log is created.
    """
    try:
        with get_db_session_sync() as db:
            analysis_service = FastingAnalysisService(db)
            success = analysis_service.analyze_meal_log(log_id, language)

            if success:
                return f"Successfully analyzed fasting meal log ID {log_id}"
            else:
                raise Exception(f"Failed to analyze fasting meal log ID {log_id}")
    except Exception as error:
        if self.request.retries >= self.max_retries:
            raise error
        else:
            self.retry(exc=error)
