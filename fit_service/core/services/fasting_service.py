from typing import List, Optional, Tuple
from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from fit_service.api.v1.fasting.fasting_schemas import (
    FastingPlanCreate,
    FastingPlanResponse,
    FastingMealLogCreate,
    FastingMealLogUpdate,
    FastingMealLogResponse,
    FastingWorkoutLogCreate,
    FastingWorkoutLogUpdate,
    FastingWorkoutLogResponse,
)
from libs import ErrorCode, ExceptionBase
from libs.models.fasting import FastingPlan, FastingMealLog, FastingWorkoutLog
from fit_service.core.worker.tasks import analyze_fasting_meal_log, analyze_fasting_workout_log
from libs.helper.space import SpaceService
from fastapi import UploadFile
from libs.models.user import User


class FastingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # FastingPlan methods
    async def create_or_update_fasting_plan(self, user_id: int, plan_data: FastingPlanCreate) -> FastingPlanResponse:
        """Create a new fasting plan or update the existing one for a user"""
        result = await self.db.execute(
            select(FastingPlan)
            .where(FastingPlan.user_id == user_id, FastingPlan.deleted_date.is_(None), FastingPlan.status == "active")
            .order_by(FastingPlan.created_date.desc())
        )
        latest_plan = result.scalars().first()

        if not latest_plan:
            # Create a new plan
            new_plan = FastingPlan(
                user_id=user_id,
                fasting_hours=plan_data.fasting_hours,
                eating_hours=plan_data.eating_hours,
                target_week=plan_data.target_week,
                target_meals=plan_data.target_meals,
                mood=plan_data.mood,
                stage=plan_data.stage,
                current_week=0,
                start_date=datetime.now(),
                finish_date=datetime.now() + timedelta(hours=plan_data.fasting_hours + plan_data.eating_hours),
            )
            self.db.add(new_plan)
            await self.db.commit()
            await self.db.refresh(new_plan)
            # Ensure current_week is an int for Pydantic validation
            plan_dict = new_plan.__dict__.copy()
            if plan_dict.get("current_week") is not None:
                plan_dict["current_week"] = int(plan_dict["current_week"])
            return FastingPlanResponse.model_validate(plan_dict)
        else:
            # Update existing plan
            latest_plan.fasting_hours = plan_data.fasting_hours
            latest_plan.eating_hours = plan_data.eating_hours
            latest_plan.target_week = plan_data.target_week
            latest_plan.target_meals = plan_data.target_meals
            latest_plan.mood = plan_data.mood
            latest_plan.stage = plan_data.stage
            latest_plan.finish_date = latest_plan.start_date + timedelta(
                hours=plan_data.fasting_hours + plan_data.eating_hours
            )
            latest_plan.status = plan_data.status or latest_plan.status
            await self.db.commit()
            await self.db.refresh(latest_plan)
            # Ensure current_week is an int for Pydantic validation
            plan_dict = latest_plan.__dict__.copy()
            if plan_dict.get("current_week") is not None:
                plan_dict["current_week"] = int(plan_dict["current_week"])
            return FastingPlanResponse.model_validate(plan_dict)

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

        # Ensure current_week is an int for Pydantic validation
        plan_dict = plan.__dict__.copy()
        if plan_dict.get("current_week") is not None:
            plan_dict["current_week"] = int(plan_dict["current_week"])
        return FastingPlanResponse.model_validate(plan_dict)

    async def list_fasting_plans(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[FastingPlanResponse], int]:
        """List all fasting plans for a user with pagination"""
        # Get total count
        count_result = await self.db.execute(
            select(func.count())
            .select_from(FastingPlan)
            .where(FastingPlan.user_id == user_id, FastingPlan.deleted_date.is_(None))
        )
        total_count = count_result.scalar_one()

        # Get plans with pagination
        result = await self.db.execute(
            select(FastingPlan)
            .where(FastingPlan.user_id == user_id, FastingPlan.deleted_date.is_(None))
            .order_by(FastingPlan.created_date.desc())
            .offset(skip)
            .limit(limit)
        )
        plans = result.scalars().all()

        return [FastingPlanResponse.model_validate(plan) for plan in plans], total_count

    # FastingMealLog methods
    async def _handle_meal_log_photo(self, photo: UploadFile) -> str:
        """Upload photo to DigitalOcean Spaces and return the file URL."""
        if photo is None:
            return None
        space_service = SpaceService()
        result = await space_service.upload_image(photo, folder="meal_photos")
        return result.get("url")

    async def create_meal_log(
        self, user_id: int, meal_data: FastingMealLogCreate, photo: UploadFile = None
    ) -> FastingMealLogResponse:
        """Create a new meal log for a fasting plan"""
        # Verify the plan exists and belongs to the user
        result = await self.db.execute(
            select(FastingPlan).where(
                FastingPlan.id == meal_data.plan_id,
                FastingPlan.user_id == user_id,
                FastingPlan.deleted_date.is_(None),
            )
        )
        plan = result.scalars().first()

        if not plan:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Get user language preference
        user_result = await self.db.execute(select(User.language).where(User.id == user_id))
        user_language = user_result.scalar_one_or_none()

        if not user_language:
            raise ExceptionBase(ErrorCode.INVALID_PARAMETERS)

        # Handle photo upload if provided
        photo_url = meal_data.photo_url
        if photo is not None:
            photo_url = await self._handle_meal_log_photo(photo)

        # Create the meal log
        new_meal_log = FastingMealLog(
            user_id=user_id,
            plan_id=meal_data.plan_id,
            title=meal_data.title,
            photo_url=photo_url,
            notes=meal_data.notes,
            calories=meal_data.calories,
            protein=meal_data.protein,
            carbs=meal_data.carbs,
            fat=meal_data.fat,
            detailed_macros=meal_data.detailed_macros,
            ai_content=meal_data.ai_content,
        )
        self.db.add(new_meal_log)
        await self.db.commit()
        await self.db.refresh(new_meal_log)

        # Trigger analysis as a background task
        analyze_fasting_meal_log.delay(new_meal_log.id, user_language)

        return FastingMealLogResponse.model_validate(new_meal_log)

    async def get_meal_log(self, log_id: int, user_id: int) -> FastingMealLogResponse:
        """Get a specific meal log by ID, ensuring it belongs to the user"""
        result = await self.db.execute(
            select(FastingMealLog).where(
                FastingMealLog.id == log_id,
                FastingMealLog.user_id == user_id,
                FastingMealLog.deleted_date.is_(None),
            )
        )
        log = result.scalars().first()

        if not log:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return FastingMealLogResponse.model_validate(log)

    async def list_meal_logs(
        self, user_id: int, plan_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> Tuple[List[FastingMealLogResponse], int]:
        """List meal logs for a user, optionally filtered by plan_id"""
        # Build the base query
        base_query = select(FastingMealLog).where(
            FastingMealLog.user_id == user_id, FastingMealLog.deleted_date.is_(None)
        )

        # Add plan_id filter if provided
        if plan_id is not None:
            base_query = base_query.where(FastingMealLog.plan_id == plan_id)

        # Get total count
        count_result = await self.db.execute(select(func.count()).select_from(base_query.subquery()))
        total_count = count_result.scalar_one()

        # Get logs with pagination
        result = await self.db.execute(
            base_query.order_by(FastingMealLog.created_date.desc()).offset(skip).limit(limit)
        )
        logs = result.scalars().all()

        return [FastingMealLogResponse.model_validate(log) for log in logs], total_count

    async def update_meal_log(
        self, log_id: int, user_id: int, meal_data: FastingMealLogUpdate, photo: UploadFile = None
    ) -> FastingMealLogResponse:
        """Update a meal log, ensuring it belongs to the user. Allows updating title, notes, and photo."""
        result = await self.db.execute(
            select(FastingMealLog).where(
                FastingMealLog.id == log_id,
                FastingMealLog.user_id == user_id,
                FastingMealLog.deleted_date.is_(None),
            )
        )
        log = result.scalars().first()

        if not log:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update only provided fields
        if meal_data.title is not None:
            log.title = meal_data.title
        if meal_data.notes is not None:
            log.notes = meal_data.notes
        if photo is not None:
            log.photo_url = await self._handle_meal_log_photo(photo)

        await self.db.commit()
        await self.db.refresh(log)
        return FastingMealLogResponse.model_validate(log)

    async def delete_meal_log(self, log_id: int, user_id: int) -> None:
        """Soft delete a meal log, ensuring it belongs to the user"""
        result = await self.db.execute(
            select(FastingMealLog).where(
                FastingMealLog.id == log_id,
                FastingMealLog.user_id == user_id,
                FastingMealLog.deleted_date.is_(None),
            )
        )
        log = result.scalars().first()

        if not log:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        log.deleted_date = datetime.now()
        await self.db.commit()

    # FastingWorkoutLog methods
    async def create_workout_log(
        self, user_id: int, workout_data: FastingWorkoutLogCreate
    ) -> FastingWorkoutLogResponse:
        """Create a new workout log for a fasting plan"""
        # Verify the plan exists and belongs to the user
        result = await self.db.execute(
            select(FastingPlan).where(
                FastingPlan.id == workout_data.plan_id,
                FastingPlan.user_id == user_id,
                FastingPlan.deleted_date.is_(None),
            )
        )
        plan = result.scalars().first()

        if not plan:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Get user language preference
        user_result = await self.db.execute(select(User.language).where(User.id == user_id))
        user_language = user_result.scalar_one_or_none()

        if not user_language:
            raise ExceptionBase(ErrorCode.INVALID_PARAMETERS)

        # Create the workout log
        new_workout_log = FastingWorkoutLog(
            user_id=user_id,
            plan_id=workout_data.plan_id,
            workout_name=workout_data.workout_name,
            duration_minutes=workout_data.duration_minutes,
            calories_burned=workout_data.calories_burned,
            intensity=workout_data.intensity,
            notes=workout_data.notes,
        )
        self.db.add(new_workout_log)
        await self.db.commit()
        await self.db.refresh(new_workout_log)

        # Trigger analysis as a background task
        analyze_fasting_workout_log.delay(new_workout_log.id, user_language)

        return FastingWorkoutLogResponse.model_validate(new_workout_log)

    async def get_workout_log(self, log_id: int, user_id: int) -> FastingWorkoutLogResponse:
        """Get a specific workout log by ID, ensuring it belongs to the user"""
        result = await self.db.execute(
            select(FastingWorkoutLog).where(
                FastingWorkoutLog.id == log_id,
                FastingWorkoutLog.user_id == user_id,
                FastingWorkoutLog.deleted_date.is_(None),
            )
        )
        log = result.scalars().first()

        if not log:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return FastingWorkoutLogResponse.model_validate(log)

    async def list_workout_logs(
        self, user_id: int, plan_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> Tuple[List[FastingWorkoutLogResponse], int]:
        """List workout logs for a user, optionally filtered by plan_id"""
        # Build the base query
        base_query = select(FastingWorkoutLog).where(
            FastingWorkoutLog.user_id == user_id, FastingWorkoutLog.deleted_date.is_(None)
        )

        # Add plan_id filter if provided
        if plan_id is not None:
            base_query = base_query.where(FastingWorkoutLog.plan_id == plan_id)

        # Get total count
        count_result = await self.db.execute(select(func.count()).select_from(base_query.subquery()))
        total_count = count_result.scalar_one()

        # Get logs with pagination
        result = await self.db.execute(
            base_query.order_by(FastingWorkoutLog.created_date.desc()).offset(skip).limit(limit)
        )
        logs = result.scalars().all()

        return [FastingWorkoutLogResponse.model_validate(log) for log in logs], total_count

    async def update_workout_log(
        self, log_id: int, user_id: int, workout_data: FastingWorkoutLogUpdate
    ) -> FastingWorkoutLogResponse:
        """Update a workout log, ensuring it belongs to the user"""
        result = await self.db.execute(
            select(FastingWorkoutLog).where(
                FastingWorkoutLog.id == log_id,
                FastingWorkoutLog.user_id == user_id,
                FastingWorkoutLog.deleted_date.is_(None),
            )
        )
        log = result.scalars().first()

        if not log:
            raise ExceptionBase(ErrorCode.NOT_FOUND, "Workout log not found")

        # Update fields if provided
        if workout_data.workout_name is not None:
            log.workout_name = workout_data.workout_name
        if workout_data.duration_minutes is not None:
            log.duration_minutes = workout_data.duration_minutes
        if workout_data.calories_burned is not None:
            log.calories_burned = workout_data.calories_burned
        if workout_data.intensity is not None:
            log.intensity = workout_data.intensity
        if workout_data.notes is not None:
            log.notes = workout_data.notes

        await self.db.commit()
        await self.db.refresh(log)

        return FastingWorkoutLogResponse.model_validate(log)

    async def delete_workout_log(self, log_id: int, user_id: int) -> None:
        """Soft delete a workout log, ensuring it belongs to the user"""
        result = await self.db.execute(
            select(FastingWorkoutLog).where(
                FastingWorkoutLog.id == log_id,
                FastingWorkoutLog.user_id == user_id,
                FastingWorkoutLog.deleted_date.is_(None),
            )
        )
        log = result.scalars().first()

        if not log:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        log.deleted_date = datetime.now()
        await self.db.commit()
