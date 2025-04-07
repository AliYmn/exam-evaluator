from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fit_service.api.v1.workout_tracker.workout_tracker_schemas import (
    WorkoutTrackerCreate,
    WorkoutTrackerUpdate,
    WorkoutTrackerResponse,
)
from libs import ErrorCode, ExceptionBase
from libs.models.workout_tracker import WorkoutTracker


class WorkoutTrackerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_workout_tracker(self, user_id: int, tracker_data: WorkoutTrackerCreate) -> None:
        """Create a new workout tracker record for a user"""
        new_tracker = WorkoutTracker(
            user_id=user_id,
            name=tracker_data.name,
            workout_id=tracker_data.workout_id,
            is_completed=tracker_data.is_completed,
            duration_minutes=tracker_data.duration_minutes,
            calories_burned=tracker_data.calories_burned,
            sets=tracker_data.sets,
            reps=tracker_data.reps,
            notes=tracker_data.notes,
            custom_data=tracker_data.custom_data,
        )
        self.db.add(new_tracker)
        await self.db.commit()
        await self.db.refresh(new_tracker)

    async def get_workout_tracker(self, tracker_id: int, user_id: int) -> Optional[WorkoutTrackerResponse]:
        """Get a specific workout tracker record by ID, ensuring it belongs to the user"""
        result = await self.db.execute(
            select(WorkoutTracker).where(
                WorkoutTracker.id == tracker_id,
                WorkoutTracker.user_id == user_id,
                WorkoutTracker.deleted_date.is_(None),
            )
        )
        tracker = result.scalars().first()
        if not tracker:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return WorkoutTrackerResponse.model_validate(tracker)

    async def list_workout_trackers(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[WorkoutTrackerResponse], int]:
        """List all workout tracker records for a user with pagination"""
        # Get total count
        count_query = select(WorkoutTracker).where(
            WorkoutTracker.user_id == user_id, WorkoutTracker.deleted_date.is_(None)
        )
        count_result = await self.db.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records
        result = await self.db.execute(
            select(WorkoutTracker)
            .where(WorkoutTracker.user_id == user_id, WorkoutTracker.deleted_date.is_(None))
            .order_by(WorkoutTracker.created_date.desc())
            .offset(skip)
            .limit(limit)
        )
        trackers = result.scalars().all()

        return [WorkoutTrackerResponse.model_validate(tracker) for tracker in trackers], total_count

    async def get_latest_workout_tracker(self, user_id: int) -> Optional[WorkoutTrackerResponse]:
        """Get the latest workout tracker record for a user"""
        result = await self.db.execute(
            select(WorkoutTracker)
            .where(WorkoutTracker.user_id == user_id, WorkoutTracker.deleted_date.is_(None))
            .order_by(WorkoutTracker.created_date.desc())
            .limit(1)
        )
        tracker = result.scalars().first()
        if not tracker:
            return None

        return WorkoutTrackerResponse.model_validate(tracker)

    async def update_workout_tracker(self, tracker_id: int, user_id: int, tracker_data: WorkoutTrackerUpdate) -> None:
        """Update a specific workout tracker record"""
        # Get the tracker record
        result = await self.db.execute(
            select(WorkoutTracker).where(
                WorkoutTracker.id == tracker_id,
                WorkoutTracker.user_id == user_id,
                WorkoutTracker.deleted_date.is_(None),
            )
        )
        tracker = result.scalars().first()
        if not tracker:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update fields
        if tracker_data.name is not None:
            tracker.name = tracker_data.name
        if tracker_data.workout_id is not None:
            tracker.workout_id = tracker_data.workout_id
        if tracker_data.is_completed is not None:
            tracker.is_completed = tracker_data.is_completed
        if tracker_data.duration_minutes is not None:
            tracker.duration_minutes = tracker_data.duration_minutes
        if tracker_data.calories_burned is not None:
            tracker.calories_burned = tracker_data.calories_burned
        if tracker_data.sets is not None:
            tracker.sets = tracker_data.sets
        if tracker_data.reps is not None:
            tracker.reps = tracker_data.reps
        if tracker_data.notes is not None:
            tracker.notes = tracker_data.notes
        if tracker_data.custom_data is not None:
            tracker.custom_data = tracker_data.custom_data

        # Save changes
        await self.db.commit()
        await self.db.refresh(tracker)

    async def delete_workout_tracker(self, tracker_id: int, user_id: int) -> None:
        """Soft delete a specific workout tracker record by setting deleted_date"""
        # Verify the tracker exists and belongs to the user
        result = await self.db.execute(
            select(WorkoutTracker).where(
                WorkoutTracker.id == tracker_id,
                WorkoutTracker.user_id == user_id,
                WorkoutTracker.deleted_date.is_(None),
            )
        )
        tracker = result.scalars().first()
        if not tracker:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Soft delete
        tracker.soft_delete()
        await self.db.commit()
