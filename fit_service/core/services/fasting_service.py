from typing import List, Optional, Tuple

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
        # Check if user already has a plan
        result = await self.db.execute(
            select(FastingPlan).where(FastingPlan.user_id == user_id, FastingPlan.deleted_date.is_(None))
        )
        existing_plan = result.scalars().first()

        if existing_plan:
            # Update existing plan
            existing_plan.fasting_hours = plan_data.fasting_hours
            existing_plan.eating_hours = plan_data.eating_hours
            existing_plan.target_week = plan_data.target_week
            await self.db.commit()
            await self.db.refresh(existing_plan)
            return FastingPlanResponse.model_validate(existing_plan)
        else:
            # Create new plan
            new_plan = FastingPlan(
                user_id=user_id,
                fasting_hours=plan_data.fasting_hours,
                eating_hours=plan_data.eating_hours,
                target_week=plan_data.target_week,
            )
            self.db.add(new_plan)
            await self.db.commit()
            await self.db.refresh(new_plan)
            return FastingPlanResponse.model_validate(new_plan)

    async def get_latest_fasting_plan(self, user_id: int) -> FastingPlanResponse:
        """Get the latest fasting plan for a user"""
        result = await self.db.execute(
            select(FastingPlan)
            .where(FastingPlan.user_id == user_id, FastingPlan.deleted_date.is_(None))
            .order_by(FastingPlan.created_date.desc())
            .limit(1)
        )
        plan = result.scalars().first()

        if not plan:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

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
            calories=meal_data.calories,
            protein=meal_data.protein,
            carbs=meal_data.carbs,
            fat=meal_data.fat,
            detailed_macros=meal_data.detailed_macros,
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
        if meal_data.calories is not None:
            meal_log.calories = meal_data.calories
        if meal_data.protein is not None:
            meal_log.protein = meal_data.protein
        if meal_data.carbs is not None:
            meal_log.carbs = meal_data.carbs
        if meal_data.fat is not None:
            meal_log.fat = meal_data.fat
        if meal_data.detailed_macros is not None:
            meal_log.detailed_macros = meal_data.detailed_macros

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
