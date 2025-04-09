from typing import List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from fit_service.api.v1.fasting.fasting_schemas import (
    FastingPlanCreate,
    FastingPlanUpdate,
    FastingPlanResponse,
    FastingSessionCreate,
    FastingSessionUpdate,
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
    async def create_fasting_plan(self, user_id: int, plan_data: FastingPlanCreate) -> FastingPlanResponse:
        """Create a new fasting plan for a user"""
        # Check if user already has an active plan
        if plan_data.is_active:
            await self._deactivate_existing_plans(user_id)

        # Create new plan
        new_plan = FastingPlan(
            user_id=user_id,
            fasting_type=plan_data.fasting_type,
            is_active=plan_data.is_active,
            target_calories=plan_data.target_calories,
            target_meals=plan_data.target_meals,
            target_water=plan_data.target_water,
            target_protein=plan_data.target_protein,
            target_carb=plan_data.target_carb,
            target_fat=plan_data.target_fat,
        )
        self.db.add(new_plan)
        await self.db.commit()
        await self.db.refresh(new_plan)

        return FastingPlanResponse.model_validate(new_plan)

    async def _deactivate_existing_plans(self, user_id: int) -> None:
        """Deactivate all existing active plans for a user"""
        result = await self.db.execute(
            select(FastingPlan).where(
                FastingPlan.user_id == user_id, FastingPlan.is_active == True, FastingPlan.deleted_date.is_(None)
            )
        )
        active_plans = result.scalars().all()

        for plan in active_plans:
            plan.is_active = False

        await self.db.commit()

    async def get_fasting_plan(self, plan_id: int, user_id: int) -> FastingPlanResponse:
        """Get a specific fasting plan by ID, ensuring it belongs to the user"""
        result = await self.db.execute(
            select(FastingPlan).where(
                FastingPlan.id == plan_id, FastingPlan.user_id == user_id, FastingPlan.deleted_date.is_(None)
            )
        )
        plan = result.scalars().first()

        if not plan:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return FastingPlanResponse.model_validate(plan)

    async def get_active_fasting_plan(self, user_id: int) -> Optional[FastingPlanResponse]:
        """Get the active fasting plan for a user"""
        result = await self.db.execute(
            select(FastingPlan).where(
                FastingPlan.user_id == user_id, FastingPlan.is_active == True, FastingPlan.deleted_date.is_(None)
            )
        )
        plan = result.scalars().first()

        if not plan:
            return None

        return FastingPlanResponse.model_validate(plan)

    async def list_fasting_plans(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[FastingPlanResponse], int]:
        """List all fasting plans for a user with pagination"""
        # Get total count
        count_query = (
            select(func.count())
            .select_from(FastingPlan)
            .where(FastingPlan.user_id == user_id, FastingPlan.deleted_date.is_(None))
        )
        total_count = await self.db.scalar(count_query)

        # Get paginated records
        result = await self.db.execute(
            select(FastingPlan)
            .where(FastingPlan.user_id == user_id, FastingPlan.deleted_date.is_(None))
            .order_by(FastingPlan.created_date.desc())
            .offset(skip)
            .limit(limit)
        )
        plans = result.scalars().all()

        return [FastingPlanResponse.model_validate(plan) for plan in plans], total_count or 0

    async def update_fasting_plan(
        self, plan_id: int, user_id: int, plan_data: FastingPlanUpdate
    ) -> FastingPlanResponse:
        """Update a specific fasting plan"""
        # Get the plan record
        result = await self.db.execute(
            select(FastingPlan).where(
                FastingPlan.id == plan_id, FastingPlan.user_id == user_id, FastingPlan.deleted_date.is_(None)
            )
        )
        plan = result.scalars().first()

        if not plan:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # If setting this plan to active, deactivate other plans
        if plan_data.is_active and not plan.is_active:
            await self._deactivate_existing_plans(user_id)

        # Update plan data
        if plan_data.fasting_type is not None:
            plan.fasting_type = plan_data.fasting_type
        if plan_data.is_active is not None:
            plan.is_active = plan_data.is_active
        if plan_data.target_calories is not None:
            plan.target_calories = plan_data.target_calories
        if plan_data.target_meals is not None:
            plan.target_meals = plan_data.target_meals
        if plan_data.target_water is not None:
            plan.target_water = plan_data.target_water
        if plan_data.target_protein is not None:
            plan.target_protein = plan_data.target_protein
        if plan_data.target_carb is not None:
            plan.target_carb = plan_data.target_carb
        if plan_data.target_fat is not None:
            plan.target_fat = plan_data.target_fat

        await self.db.commit()
        await self.db.refresh(plan)

        return FastingPlanResponse.model_validate(plan)

    async def delete_fasting_plan(self, plan_id: int, user_id: int) -> None:
        """Soft delete a specific fasting plan by setting deleted_date"""
        # Verify the plan exists and belongs to the user
        result = await self.db.execute(
            select(FastingPlan).where(
                FastingPlan.id == plan_id, FastingPlan.user_id == user_id, FastingPlan.deleted_date.is_(None)
            )
        )
        plan = result.scalars().first()

        if not plan:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Soft delete by setting deleted_date
        plan.deleted_date = datetime.now()
        await self.db.commit()

    # FastingSession methods
    async def create_fasting_session(self, user_id: int, session_data: FastingSessionCreate) -> FastingSessionResponse:
        """Create a new fasting session for a user"""
        # Check if there's already an active session
        active_session = await self._get_active_session(user_id)
        if active_session:
            raise ExceptionBase(ErrorCode.CONFLICT, "User already has an active fasting session")

        # Create new session
        new_session = FastingSession(
            user_id=user_id,
            plan_id=session_data.plan_id,
            start_time=session_data.start_time,
            end_time=session_data.end_time,
            status="STARTED",  # Default status for new sessions
            mood=session_data.mood,
            stage=session_data.stage,
        )
        self.db.add(new_session)
        await self.db.commit()
        await self.db.refresh(new_session)

        return FastingSessionResponse.model_validate(new_session)

    async def _get_active_session(self, user_id: int) -> Optional[FastingSession]:
        """Get the active fasting session for a user if one exists"""
        result = await self.db.execute(
            select(FastingSession).where(
                FastingSession.user_id == user_id,
                FastingSession.status.in_(["PENDING", "STARTED"]),
                FastingSession.deleted_date.is_(None),
            )
        )
        return result.scalars().first()

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
        """Get the most recent fasting session for a user"""
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
        total_count = await self.db.scalar(count_query)

        # Get paginated records
        result = await self.db.execute(
            select(FastingSession)
            .where(FastingSession.user_id == user_id, FastingSession.deleted_date.is_(None))
            .order_by(FastingSession.created_date.desc())
            .offset(skip)
            .limit(limit)
        )
        sessions = result.scalars().all()

        return [FastingSessionResponse.model_validate(session) for session in sessions], total_count or 0

    async def update_fasting_session(
        self, session_id: int, user_id: int, session_data: FastingSessionUpdate
    ) -> FastingSessionResponse:
        """Update a specific fasting session"""
        # Get the session record
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

        # Update session data
        if session_data.end_time is not None:
            session.end_time = session_data.end_time
        if session_data.status is not None:
            session.status = session_data.status
        if session_data.mood is not None:
            session.mood = session_data.mood
        if session_data.stage is not None:
            session.stage = session_data.stage

        await self.db.commit()
        await self.db.refresh(session)

        return FastingSessionResponse.model_validate(session)

    async def delete_fasting_session(self, session_id: int, user_id: int) -> None:
        """Soft delete a specific fasting session by setting deleted_date"""
        # Verify the session exists and belongs to the user
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

        # Soft delete by setting deleted_date
        session.deleted_date = datetime.now()
        await self.db.commit()

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
