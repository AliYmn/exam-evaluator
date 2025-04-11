from datetime import datetime, timedelta

from sqlalchemy import select, distinct, update
from sqlalchemy.orm import Session

from libs.models.fasting import FastingPlan
from libs.models import Notification
from libs.models import User


class FastingScheduleService:
    def __init__(self, db: Session):
        self.db = db

    def get_users_with_active_plans(self):
        """Get all users who have active fasting plans"""
        # Query for users with active fasting plans
        result = self.db.execute(
            select(distinct(FastingPlan.user_id)).where(
                FastingPlan.status == "active",
                FastingPlan.deleted_date.is_(None),
                FastingPlan.finish_date < datetime.now(),
            )
        )
        user_ids = [row[0] for row in result.all()]
        return user_ids

    def check_user_fasting_plans(self, user_id: int):
        """Check and update fasting plans for a specific user"""
        now = datetime.now()

        # Find expired active plans for this user that are not already being processed
        result = self.db.execute(
            select(FastingPlan).where(
                FastingPlan.user_id == user_id,
                FastingPlan.status == "active",
                FastingPlan.finish_date <= now,
                FastingPlan.deleted_date.is_(None),
            )
        )
        expired_plans = result.scalars().all()

        # If no expired plans, return early
        if not expired_plans:
            return 0

        # Mark plans as being processed to prevent duplicate processing in retry scenarios
        plan_ids = [plan.id for plan in expired_plans]
        self.db.execute(update(FastingPlan).where(FastingPlan.id.in_(plan_ids)).values(status="processing"))
        self.db.commit()

        updated_plans = 0

        for plan in expired_plans:
            try:
                # Calculate current_week based on start_date progress
                if plan.start_date and plan.target_week:
                    days_passed = (now - plan.start_date).days

                    # Calculate progress as a float (e.g., 1.3 weeks)
                    current_week_float = days_passed / 7.0
                    plan.current_week = current_week_float

                # Check if target week is reached
                if plan.target_week is not None and plan.current_week >= plan.target_week:
                    # Target week reached, mark plan as completed
                    plan.status = "completed"

                    # Create completion notification
                    self._create_notification(
                        user_id=plan.user_id,
                        title="Fasting Plan Completed",
                        message=f"Congratulations! You've completed your {plan.target_week} week fasting plan.",
                        n_type="success",
                        target_screen="fasting_detail",
                    )
                else:
                    # Target week not yet reached, create new plan
                    plan.status = "inactive"

                    # Create new plan
                    new_plan = FastingPlan(
                        user_id=plan.user_id,
                        fasting_hours=plan.fasting_hours,
                        eating_hours=plan.eating_hours,
                        target_week=plan.target_week,
                        current_week=plan.current_week,
                        status="active",
                        target_calories=plan.target_calories,
                        target_meals=plan.target_meals,
                        target_water=plan.target_water,
                        target_protein=plan.target_protein,
                        target_carb=plan.target_carb,
                        target_fat=plan.target_fat,
                        mood=plan.mood,
                        stage=plan.stage,
                        start_date=plan.start_date,
                        finish_date=now + timedelta(hours=plan.fasting_hours + plan.eating_hours),
                    )
                    self.db.add(new_plan)

                    # Create new cycle notification
                    self._create_notification(
                        user_id=plan.user_id,
                        title="New Fasting Cycle Started",
                        message=f"Week {round(plan.current_week, 1)} of your fasting plan has started. Keep going!",
                        n_type="info",
                        target_screen="fasting_detail",
                    )

                # Save changes
                self.db.commit()
                updated_plans += 1
            except Exception as e:
                # If an error occurs, revert the plan status to active
                plan.status = "active"
                self.db.commit()
                # Re-raise the exception for the task to handle
                raise e

        return updated_plans

    def _create_notification(
        self, user_id: int, title: str, message: str, n_type: str = "info", target_screen: str = None
    ):
        """Create a notification for a specific user"""
        notification = Notification(
            title=title, message=message, n_type=n_type, target_screen=target_screen, icon="fasting"
        )

        # Add the user to the notification
        result = self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if user:
            notification.users.append(user)
            self.db.add(notification)
            self.db.commit()
            return notification

        return None
