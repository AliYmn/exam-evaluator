from typing import List, Optional, Tuple
from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from fit_service.api.v1.fasting.fasting_schemas import (
    FastingPlanCreate,
    FastingPlanResponse,
    FastingSessionResponse,
    FastingMealLogCreate,
    FastingMealLogUpdate,
    FastingMealLogResponse,
    FastingWorkoutLogCreate,
    FastingWorkoutLogUpdate,
    FastingWorkoutLogResponse,
)
from libs import ErrorCode, ExceptionBase
from libs.models.fasting import FastingPlan, FastingSession, FastingMealLog, FastingWorkoutLog


class FastingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # FastingPlan methods
    async def create_or_update_fasting_plan(self, user_id: int, plan_data: FastingPlanCreate) -> FastingPlanResponse:
        """Create a new fasting plan or update the existing one for a user"""
        # Get the latest fasting plan for the user
        result = await self.db.execute(
            select(FastingPlan)
            .where(FastingPlan.user_id == user_id, FastingPlan.deleted_date.is_(None))
            .order_by(FastingPlan.created_date.desc())
        )
        latest_plan = result.scalars().first()

        # Set start_date to today if not provided
        today = datetime.now()
        start_date = plan_data.start_date or today

        # Calculate finish_date based on fasting_hours + eating_hours (one cycle) * target_week
        total_hours = plan_data.fasting_hours + plan_data.eating_hours

        # If target_week is provided, multiply by the number of weeks
        if plan_data.target_week and plan_data.target_week > 0:
            total_hours = total_hours * plan_data.target_week

        finish_date = start_date + timedelta(hours=total_hours)

        # Check if we need to create a new plan
        should_create_new_plan = False  # Default to updating existing plan

        if latest_plan:
            # Get the latest plan's target_week and current_week
            target_week = latest_plan.target_week
            current_week = latest_plan.current_week

            # If current_week >= target_week, create a new plan
            if current_week is not None and target_week is not None:
                if current_week >= target_week:
                    # Current week is equal to or greater than target week, create new plan
                    should_create_new_plan = True
                else:
                    # Current week is less than target week, update existing plan
                    should_create_new_plan = False
            else:
                # Missing week data, update existing plan
                should_create_new_plan = False
        else:
            # No existing plan, create a new one
            should_create_new_plan = True

        if should_create_new_plan:
            # Create a new plan
            new_plan = FastingPlan(
                user_id=user_id,
                fasting_hours=plan_data.fasting_hours,
                eating_hours=plan_data.eating_hours,
                target_week=plan_data.target_week,
                current_week=0,
                start_date=start_date,
                finish_date=finish_date,
            )
            self.db.add(new_plan)
            await self.db.commit()
            await self.db.refresh(new_plan)
            plan_response = FastingPlanResponse.model_validate(new_plan)

            # Create a new session for this plan with current_week = 0
            await self.create_or_update_fasting_session(user_id, new_plan.id, plan_data, current_week=0)

            return plan_response
        else:
            # Update existing plan
            latest_plan.fasting_hours = plan_data.fasting_hours
            latest_plan.eating_hours = plan_data.eating_hours
            latest_plan.target_week = plan_data.target_week
            # Don't update current_week for existing plan
            latest_plan.start_date = start_date
            latest_plan.finish_date = finish_date
            await self.db.commit()
            await self.db.refresh(latest_plan)
            plan_response = FastingPlanResponse.model_validate(latest_plan)

            # Update active session if exists
            await self.create_or_update_fasting_session(user_id, latest_plan.id, plan_data)

            return plan_response

    async def create_or_update_fasting_session(
        self, user_id: int, plan_id: int, plan_data: FastingPlanCreate, current_week: int = None
    ) -> None:
        """Create a new fasting session or update the active one for a user"""
        # Check if user has an active session
        result = await self.db.execute(
            select(FastingSession)
            .where(
                FastingSession.user_id == user_id,
                FastingSession.status == "active",
                FastingSession.deleted_date.is_(None),
            )
            .order_by(FastingSession.created_date.desc())
        )
        active_session = result.scalars().first()

        current_time = datetime.now().time()

        if active_session and current_week is None:
            # Update existing session
            active_session.plan_id = plan_id
            active_session.fasting_hours = plan_data.fasting_hours
            active_session.eating_hours = plan_data.eating_hours
            active_session.target_week = plan_data.target_week
            # Don't update current_week for existing sessions
            await self.db.commit()
        else:
            # Create new session with current_week = 0 or specified value
            new_session = FastingSession(
                user_id=user_id,
                plan_id=plan_id,
                start_time=current_time,
                status="active",
                fasting_hours=plan_data.fasting_hours,
                eating_hours=plan_data.eating_hours,
                target_week=plan_data.target_week,
                current_week=0 if current_week is None else current_week,  # Start with week 0 or specified value
            )
            self.db.add(new_session)
            await self.db.commit()

    async def get_latest_fasting_plan(self, user_id: int) -> Optional[FastingPlanResponse]:
        """Get the latest fasting plan for a user"""
        result = await self.db.execute(
            select(FastingPlan)
            .where(FastingPlan.user_id == user_id, FastingPlan.deleted_date.is_(None))
            .order_by(FastingPlan.created_date.desc())
            .limit(1)
        )
        plan = result.scalars().first()

        if not plan:
            return None

        return FastingPlanResponse.model_validate(plan)

    # FastingSession methods
    async def get_fasting_session(self, session_id: int, user_id: int) -> FastingSessionResponse:
        """Get a specific fasting session by ID, ensuring it belongs to the user"""
        result = await self.db.execute(
            select(FastingSession).where(
                FastingSession.id == session_id,
                FastingSession.user_id == user_id,
                FastingSession.deleted_date.is_(None),
            )
        )
        session = result.scalars().first()

        if not session:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return FastingSessionResponse.model_validate(session)

    async def get_latest_fasting_session(self, user_id: int) -> Optional[FastingSessionResponse]:
        """Get the latest fasting session for a user"""
        result = await self.db.execute(
            select(FastingSession)
            .where(FastingSession.user_id == user_id, FastingSession.deleted_date.is_(None))
            .order_by(FastingSession.created_date.desc())
            .limit(1)
        )
        session = result.scalars().first()

        if not session:
            return None

        return FastingSessionResponse.model_validate(session)

    async def list_fasting_sessions(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[FastingSessionResponse], int]:
        """List all fasting sessions for a user with pagination"""
        # Get total count
        count_query = (
            select(func.count())
            .select_from(FastingSession)
            .where(FastingSession.user_id == user_id, FastingSession.deleted_date.is_(None))
        )
        total_count = await self.db.execute(count_query)
        total = total_count.scalar()

        # Get sessions with pagination
        query = (
            select(FastingSession)
            .where(FastingSession.user_id == user_id, FastingSession.deleted_date.is_(None))
            .order_by(FastingSession.created_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        sessions = result.scalars().all()

        return [FastingSessionResponse.model_validate(session) for session in sessions], total

    # Fasting Meal Log Methods
    async def create_meal_log(self, user_id: int, meal_data: FastingMealLogCreate) -> FastingMealLogResponse:
        """Create a new meal log for a fasting session"""
        # Verify the session exists and belongs to the user
        await self._verify_session_ownership(user_id, meal_data.session_id)

        # Create new meal log
        new_meal_log = FastingMealLog(
            user_id=user_id,
            session_id=meal_data.session_id,
            photo_url=meal_data.photo_url,
            notes=meal_data.notes,
        )

        self.db.add(new_meal_log)
        await self.db.commit()
        await self.db.refresh(new_meal_log)

        return FastingMealLogResponse.model_validate(new_meal_log)

    async def get_meal_log(self, log_id: int, user_id: int) -> FastingMealLogResponse:
        """Get a specific meal log by ID"""
        result = await self.db.execute(
            select(FastingMealLog).where(
                FastingMealLog.id == log_id,
                FastingMealLog.user_id == user_id,
            )
        )
        meal_log = result.scalars().first()

        if not meal_log:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return FastingMealLogResponse.model_validate(meal_log)

    async def list_meal_logs(
        self, user_id: int, session_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> Tuple[List[FastingMealLogResponse], int]:
        """List meal logs for a user, optionally filtered by session"""
        query = select(FastingMealLog).where(FastingMealLog.user_id == user_id)

        if session_id:
            query = query.where(FastingMealLog.session_id == session_id)

        query = query.order_by(FastingMealLog.created_date.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        logs = result.scalars().all()

        return [FastingMealLogResponse.model_validate(log) for log in logs], len(logs)

    async def update_meal_log(
        self, log_id: int, user_id: int, meal_data: FastingMealLogUpdate
    ) -> FastingMealLogResponse:
        """Update an existing meal log"""
        result = await self.db.execute(
            select(FastingMealLog).where(
                FastingMealLog.id == log_id,
                FastingMealLog.user_id == user_id,
            )
        )
        meal_log = result.scalars().first()

        if not meal_log:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update fields if provided
        if meal_data.photo_url is not None:
            meal_log.photo_url = meal_data.photo_url
        if meal_data.notes is not None:
            meal_log.notes = meal_data.notes

        await self.db.commit()
        await self.db.refresh(meal_log)

        return FastingMealLogResponse.model_validate(meal_log)

    async def delete_meal_log(self, log_id: int, user_id: int) -> None:
        """Delete a meal log"""
        result = await self.db.execute(
            select(FastingMealLog).where(
                FastingMealLog.id == log_id,
                FastingMealLog.user_id == user_id,
            )
        )
        meal_log = result.scalars().first()

        if not meal_log:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        await self.db.delete(meal_log)
        await self.db.commit()

    # Fasting Workout Log Methods
    async def create_workout_log(
        self, user_id: int, workout_data: FastingWorkoutLogCreate
    ) -> FastingWorkoutLogResponse:
        """Create a new workout log for a fasting session"""
        # Verify the session exists and belongs to the user
        await self._verify_session_ownership(user_id, workout_data.session_id)

        # Create new workout log
        new_workout_log = FastingWorkoutLog(
            user_id=user_id,
            session_id=workout_data.session_id,
            workout_name=workout_data.workout_name,
            duration_minutes=workout_data.duration_minutes,
            calories_burned=workout_data.calories_burned,
            intensity=workout_data.intensity,
            notes=workout_data.notes,
        )

        self.db.add(new_workout_log)
        await self.db.commit()
        await self.db.refresh(new_workout_log)

        return FastingWorkoutLogResponse.model_validate(new_workout_log)

    async def get_workout_log(self, log_id: int, user_id: int) -> FastingWorkoutLogResponse:
        """Get a specific workout log by ID"""
        result = await self.db.execute(
            select(FastingWorkoutLog).where(
                FastingWorkoutLog.id == log_id,
                FastingWorkoutLog.user_id == user_id,
            )
        )
        workout_log = result.scalars().first()

        if not workout_log:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return FastingWorkoutLogResponse.model_validate(workout_log)

    async def list_workout_logs(
        self, user_id: int, session_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> Tuple[List[FastingWorkoutLogResponse], int]:
        """List workout logs for a user, optionally filtered by session"""
        query = select(FastingWorkoutLog).where(FastingWorkoutLog.user_id == user_id)

        if session_id:
            query = query.where(FastingWorkoutLog.session_id == session_id)

        query = query.order_by(FastingWorkoutLog.created_date.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        logs = result.scalars().all()

        return [FastingWorkoutLogResponse.model_validate(log) for log in logs], len(logs)

    async def update_workout_log(
        self, log_id: int, user_id: int, workout_data: FastingWorkoutLogUpdate
    ) -> FastingWorkoutLogResponse:
        """Update an existing workout log"""
        result = await self.db.execute(
            select(FastingWorkoutLog).where(
                FastingWorkoutLog.id == log_id,
                FastingWorkoutLog.user_id == user_id,
            )
        )
        workout_log = result.scalars().first()

        if not workout_log:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update fields if provided
        if workout_data.workout_name is not None:
            workout_log.workout_name = workout_data.workout_name
        if workout_data.duration_minutes is not None:
            workout_log.duration_minutes = workout_data.duration_minutes
        if workout_data.calories_burned is not None:
            workout_log.calories_burned = workout_data.calories_burned
        if workout_data.intensity is not None:
            workout_log.intensity = workout_data.intensity
        if workout_data.notes is not None:
            workout_log.notes = workout_data.notes

        await self.db.commit()
        await self.db.refresh(workout_log)

        return FastingWorkoutLogResponse.model_validate(workout_log)

    async def delete_workout_log(self, log_id: int, user_id: int) -> None:
        """Delete a workout log"""
        result = await self.db.execute(
            select(FastingWorkoutLog).where(
                FastingWorkoutLog.id == log_id,
                FastingWorkoutLog.user_id == user_id,
            )
        )
        workout_log = result.scalars().first()

        if not workout_log:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        await self.db.delete(workout_log)
        await self.db.commit()

    # Helper Methods
    async def _verify_session_ownership(self, user_id: int, session_id: int) -> None:
        """Verify that a session exists and belongs to the user"""
        result = await self.db.execute(
            select(FastingSession).where(
                FastingSession.id == session_id,
                FastingSession.user_id == user_id,
                FastingSession.deleted_date.is_(None),
            )
        )
        session = result.scalars().first()

        if not session:
            raise ExceptionBase(ErrorCode.NOT_FOUND)
