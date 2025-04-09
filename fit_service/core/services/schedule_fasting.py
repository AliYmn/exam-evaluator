from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from libs.models.fasting import FastingPlan, FastingSession


class ScheduleFastingService:
    def __init__(self, db: Session):
        self.db = db

    def check_and_update_fasting_plans(self) -> tuple[int, int]:
        """
        Check all active fasting plans and create new sessions if needed.
        This method checks if any fasting plan has reached its finish date and creates
        a new session if needed, marking the previous session as completed.

        Returns:
            tuple: (completed_plans_count, new_sessions_count)
        """
        today = datetime.now()
        completed_plans = 0
        new_sessions = 0

        # Get all active fasting plans that have a finish date of today or earlier
        query = select(FastingPlan).where(
            and_(
                FastingPlan.deleted_date.is_(None),
                FastingPlan.finish_date.isnot(None),
                FastingPlan.finish_date <= today,
            )
        )

        result = self.db.execute(query)
        plans = result.scalars().all()

        for plan in plans:
            # Find the active session for this plan
            session_query = (
                select(FastingSession)
                .where(
                    and_(
                        FastingSession.user_id == plan.user_id,
                        FastingSession.status == "active",
                        FastingSession.deleted_date.is_(None),
                    )
                )
                .order_by(FastingSession.created_date.desc())
            )

            session_result = self.db.execute(session_query)
            active_session = session_result.scalars().first()

            if active_session:
                # Check if we've reached target_week
                should_create_new_session = True
                if plan.target_week and active_session.current_week:
                    if active_session.current_week >= plan.target_week:
                        # We've reached the target, don't create a new session
                        should_create_new_session = False

                # Complete the current session
                completed_plans += self._complete_session(active_session)

                if should_create_new_session:
                    # Create a new session
                    new_sessions += self._create_new_session(plan, active_session.current_week)

                    # Update current_week for the plan
                    self._update_current_week(plan)

        return completed_plans, new_sessions

    def _complete_session(self, session: FastingSession) -> int:
        """Mark a session as completed"""
        session.status = "completed"
        session.end_time = datetime.now().time()
        self.db.commit()
        return 1

    def _create_new_session(self, plan: FastingPlan, previous_week: int = None) -> int:
        """Create a new session for a plan"""
        current_time = datetime.now().time()

        # Calculate current_week
        current_week = 1
        if previous_week is not None:
            current_week = previous_week + 1

        new_session = FastingSession(
            user_id=plan.user_id,
            plan_id=plan.id,
            start_time=current_time,
            status="active",
            fasting_hours=plan.fasting_hours,
            eating_hours=plan.eating_hours,
            target_week=plan.target_week,
            current_week=current_week,
        )
        self.db.add(new_session)
        self.db.commit()
        return 1

    def _update_current_week(self, plan: FastingPlan) -> None:
        """
        Update the current_week value of the plan.
        Increments by 1/7 daily, and resets to 1 at the end of the week.
        """
        today = datetime.now()

        # Initialize current_week if not set
        if plan.current_week is None:
            plan.current_week = 0

        # Get day of the week (0 is Monday, 6 is Sunday)
        day_of_week = today.weekday()

        # Calculate daily increment (1/7 of a week)
        daily_increment = 1 / 7

        # If it's Sunday (day 6), reset to next week
        if day_of_week == 6:  # Sunday
            # Round to nearest integer and add 1 for next week
            plan.current_week = int(plan.current_week) + 1
        else:
            # Add daily increment
            plan.current_week += daily_increment

            # Round to 2 decimal places for cleaner values
            plan.current_week = round(plan.current_week, 2)

        self.db.commit()
