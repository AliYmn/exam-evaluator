from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from fit_service.api.v1.workout.workout_schemas import WorkoutCreate, WorkoutUpdate, WorkoutResponse
from libs import ErrorCode, ExceptionBase
from libs.models.workout import Workout


class WorkoutService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_workout(self, workout_data: WorkoutCreate) -> WorkoutResponse:
        """Create a new workout record"""
        new_workout = Workout(
            name=workout_data.name,
            description=workout_data.description,
            workout_type=workout_data.workout_type,
            target_muscles=workout_data.target_muscles,
            duration_minutes=workout_data.duration_minutes,
            calories_burned=workout_data.calories_burned,
            equipment=workout_data.equipment,
            difficulty=workout_data.difficulty,
            instructions=workout_data.instructions,
        )
        self.db.add(new_workout)
        await self.db.commit()
        await self.db.refresh(new_workout)

        return WorkoutResponse.model_validate(new_workout)

    async def get_workout(self, workout_id: int) -> Optional[WorkoutResponse]:
        """Get a specific workout record by ID"""
        result = await self.db.execute(select(Workout).where(Workout.id == workout_id, Workout.deleted_date.is_(None)))
        workout = result.scalars().first()

        if not workout:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return WorkoutResponse.model_validate(workout)

    async def list_workouts(self, skip: int = 0, limit: int = 100) -> tuple[List[WorkoutResponse], int]:
        """List all workout records with pagination"""
        # Get total count
        count_query = select(Workout).where(Workout.deleted_date.is_(None))
        count_result = await self.db.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records
        result = await self.db.execute(select(Workout).where(Workout.deleted_date.is_(None)).offset(skip).limit(limit))
        workouts = result.scalars().all()

        return [WorkoutResponse.model_validate(workout) for workout in workouts], total_count

    async def update_workout(self, workout_id: int, workout_data: WorkoutUpdate) -> WorkoutResponse:
        """Update a specific workout record"""
        # Get the workout record
        result = await self.db.execute(select(Workout).where(Workout.id == workout_id, Workout.deleted_date.is_(None)))
        workout = result.scalars().first()

        if not workout:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update workout data
        if workout_data.name is not None:
            workout.name = workout_data.name
        if workout_data.description is not None:
            workout.description = workout_data.description
        if workout_data.workout_type is not None:
            workout.workout_type = workout_data.workout_type
        if workout_data.target_muscles:
            workout.target_muscles = workout_data.target_muscles
        if workout_data.duration_minutes is not None:
            workout.duration_minutes = workout_data.duration_minutes
        if workout_data.calories_burned is not None:
            workout.calories_burned = workout_data.calories_burned
        if workout_data.equipment is not None:
            workout.equipment = workout_data.equipment
        if workout_data.difficulty is not None:
            workout.difficulty = workout_data.difficulty
        if workout_data.instructions:
            workout.instructions = workout_data.instructions

        await self.db.commit()
        await self.db.refresh(workout)

        return WorkoutResponse.model_validate(workout)

    async def delete_workout(self, workout_id: int) -> None:
        """Soft delete a specific workout record by setting deleted_date"""
        # Verify the workout exists
        result = await self.db.execute(select(Workout).where(Workout.id == workout_id, Workout.deleted_date.is_(None)))
        workout = result.scalars().first()

        if not workout:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Soft delete by setting deleted_date
        workout.deleted_date = datetime.now()
        await self.db.commit()

    async def find_workouts_by_name(
        self, name: str, skip: int = 0, limit: int = 100
    ) -> tuple[List[WorkoutResponse], int]:
        """Find workouts by name (partial match)"""
        search_term = f"%{name}%"

        # Get total count
        count_query = select(Workout).where(Workout.name.ilike(search_term), Workout.deleted_date.is_(None))
        count_result = await self.db.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records
        result = await self.db.execute(
            select(Workout)
            .where(Workout.name.ilike(search_term), Workout.deleted_date.is_(None))
            .offset(skip)
            .limit(limit)
        )
        workouts = result.scalars().all()

        return [WorkoutResponse.model_validate(workout) for workout in workouts], total_count

    async def find_workouts_by_type(
        self, workout_type: str, skip: int = 0, limit: int = 100
    ) -> tuple[List[WorkoutResponse], int]:
        """Find workouts by type"""
        # Get total count
        count_query = select(Workout).where(Workout.workout_type == workout_type, Workout.deleted_date.is_(None))
        count_result = await self.db.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records
        result = await self.db.execute(
            select(Workout)
            .where(Workout.workout_type == workout_type, Workout.deleted_date.is_(None))
            .offset(skip)
            .limit(limit)
        )
        workouts = result.scalars().all()

        return [WorkoutResponse.model_validate(workout) for workout in workouts], total_count

    async def find_workouts_by_difficulty(
        self, difficulty: str, skip: int = 0, limit: int = 100
    ) -> tuple[List[WorkoutResponse], int]:
        """Find workouts by difficulty level"""
        # Get total count
        count_query = select(Workout).where(Workout.difficulty == difficulty, Workout.deleted_date.is_(None))
        count_result = await self.db.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records
        result = await self.db.execute(
            select(Workout)
            .where(Workout.difficulty == difficulty, Workout.deleted_date.is_(None))
            .offset(skip)
            .limit(limit)
        )
        workouts = result.scalars().all()

        return [WorkoutResponse.model_validate(workout) for workout in workouts], total_count
