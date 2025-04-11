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
                status="active",  # Set status to active for new plan
            )
            self.db.add(new_plan)
            await self.db.commit()
            await self.db.refresh(new_plan)
            return FastingPlanResponse.model_validate(new_plan)
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
            return FastingPlanResponse.model_validate(latest_plan)

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
    async def create_meal_log(self, user_id: int, meal_data: FastingMealLogCreate) -> FastingMealLogResponse:
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
            raise ExceptionBase(ErrorCode.NOT_FOUND, "Fasting plan not found")

        # Create the meal log
        new_meal_log = FastingMealLog(
            user_id=user_id,
            plan_id=meal_data.plan_id,
            photo_url=meal_data.photo_url,
            notes=meal_data.notes,
        )
        self.db.add(new_meal_log)
        await self.db.commit()
        await self.db.refresh(new_meal_log)

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
            raise ExceptionBase(ErrorCode.NOT_FOUND, "Meal log not found")

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
        self, log_id: int, user_id: int, meal_data: FastingMealLogUpdate
    ) -> FastingMealLogResponse:
        """Update a meal log, ensuring it belongs to the user"""
        result = await self.db.execute(
            select(FastingMealLog).where(
                FastingMealLog.id == log_id,
                FastingMealLog.user_id == user_id,
                FastingMealLog.deleted_date.is_(None),
            )
        )
        log = result.scalars().first()

        if not log:
            raise ExceptionBase(ErrorCode.NOT_FOUND, "Meal log not found")

        # Update fields if provided
        if meal_data.photo_url is not None:
            log.photo_url = meal_data.photo_url
        if meal_data.notes is not None:
            log.notes = meal_data.notes

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
            raise ExceptionBase(ErrorCode.NOT_FOUND, "Meal log not found")

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
            raise ExceptionBase(ErrorCode.NOT_FOUND, "Fasting plan not found")

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
            raise ExceptionBase(ErrorCode.NOT_FOUND, "Workout log not found")

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
            raise ExceptionBase(ErrorCode.NOT_FOUND, "Workout log not found")

        log.deleted_date = datetime.now()
        await self.db.commit()
