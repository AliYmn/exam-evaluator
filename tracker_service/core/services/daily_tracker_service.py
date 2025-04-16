from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from tracker_service.api.v1.daily_tracker.daily_tracker_schemas import (
    DailyTrackerCreate,
    DailyTrackerUpdate,
    DailyTrackerResponse,
)
from libs import ErrorCode, ExceptionBase
from libs.models.daily_tracker import DailyTracker
from tracker_service.core.worker.tasks import analyze_daily_tracker


class DailyTrackerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_daily_tracker(self, user_id: int, tracker_data: DailyTrackerCreate) -> None:
        """Create a new daily tracker record for a user"""
        new_tracker = DailyTracker(
            user_id=user_id,
            energy=tracker_data.energy,
            sleep=tracker_data.sleep,
            stress=tracker_data.stress,
            muscle_soreness=tracker_data.muscle_soreness,
            fatigue=tracker_data.fatigue,
            hunger=tracker_data.hunger,
            water_intake_liters=tracker_data.water_intake_liters,
            sleep_hours=tracker_data.sleep_hours,
            mood=tracker_data.mood,
            training_quality=tracker_data.training_quality,
            diet_compliance=tracker_data.diet_compliance,
        )
        self.db.add(new_tracker)
        await self.db.commit()
        await self.db.refresh(new_tracker)

        # Trigger analysis as a background task
        analyze_daily_tracker.delay(new_tracker.id, user_id)

    async def get_daily_tracker(self, tracker_id: int, user_id: int) -> Optional[DailyTrackerResponse]:
        """Get a specific daily tracker record by ID, ensuring it belongs to the user"""
        result = await self.db.execute(
            select(DailyTracker).where(
                DailyTracker.id == tracker_id, DailyTracker.user_id == user_id, DailyTracker.deleted_date.is_(None)
            )
        )
        tracker = result.scalars().first()

        if not tracker:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return DailyTrackerResponse.model_validate(tracker)

    async def list_daily_trackers(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[List[DailyTrackerResponse], int]:
        """List all daily tracker records for a user with pagination"""
        # Get total count
        count_query = select(DailyTracker).where(DailyTracker.user_id == user_id, DailyTracker.deleted_date.is_(None))
        count_result = await self.db.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records
        result = await self.db.execute(
            select(DailyTracker)
            .where(DailyTracker.user_id == user_id, DailyTracker.deleted_date.is_(None))
            .order_by(DailyTracker.created_date.desc())
            .offset(skip)
            .limit(limit)
        )
        trackers = result.scalars().all()

        return [DailyTrackerResponse.model_validate(tracker) for tracker in trackers], total_count

    async def update_daily_tracker(self, tracker_id: int, user_id: int, tracker_data: DailyTrackerUpdate) -> None:
        """Update a specific daily tracker record"""
        # Get the tracker record
        result = await self.db.execute(
            select(DailyTracker).where(
                DailyTracker.id == tracker_id, DailyTracker.user_id == user_id, DailyTracker.deleted_date.is_(None)
            )
        )
        tracker = result.scalars().first()

        if not tracker:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update tracker data
        if tracker_data.energy is not None:
            tracker.energy = tracker_data.energy
        if tracker_data.sleep is not None:
            tracker.sleep = tracker_data.sleep
        if tracker_data.stress is not None:
            tracker.stress = tracker_data.stress
        if tracker_data.muscle_soreness is not None:
            tracker.muscle_soreness = tracker_data.muscle_soreness
        if tracker_data.fatigue is not None:
            tracker.fatigue = tracker_data.fatigue
        if tracker_data.hunger is not None:
            tracker.hunger = tracker_data.hunger
        if tracker_data.water_intake_liters is not None:
            tracker.water_intake_liters = tracker_data.water_intake_liters
        if tracker_data.sleep_hours is not None:
            tracker.sleep_hours = tracker_data.sleep_hours
        if tracker_data.mood is not None:
            tracker.mood = tracker_data.mood
        if tracker_data.training_quality is not None:
            tracker.training_quality = tracker_data.training_quality
        if tracker_data.diet_compliance is not None:
            tracker.diet_compliance = tracker_data.diet_compliance

        await self.db.commit()
        await self.db.refresh(tracker)

    async def delete_daily_tracker(self, tracker_id: int, user_id: int) -> None:
        """Soft delete a specific daily tracker record by setting deleted_date"""
        # Verify the tracker exists and belongs to the user
        result = await self.db.execute(
            select(DailyTracker).where(
                DailyTracker.id == tracker_id, DailyTracker.user_id == user_id, DailyTracker.deleted_date.is_(None)
            )
        )
        tracker = result.scalars().first()

        if not tracker:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Soft delete by setting deleted_date
        tracker.deleted_date = datetime.now()
        await self.db.commit()

    async def get_latest_daily_tracker(self, user_id: int) -> Optional[DailyTrackerResponse]:
        """Get the most recent daily tracker record for a user"""
        result = await self.db.execute(
            select(DailyTracker)
            .where(DailyTracker.user_id == user_id, DailyTracker.deleted_date.is_(None))
            .order_by(DailyTracker.created_date.desc())
            .limit(1)
        )
        tracker = result.scalars().first()

        if not tracker:
            return None

        return DailyTrackerResponse.model_validate(tracker)

    async def analyze_daily_tracker(self, tracker_id: int, user_id: int) -> Optional[DailyTrackerResponse]:
        """Analyze a specific daily tracker record and update its AI content"""
        # First verify the tracker exists and belongs to the user
        result = await self.db.execute(
            select(DailyTracker).where(
                DailyTracker.id == tracker_id, DailyTracker.user_id == user_id, DailyTracker.deleted_date.is_(None)
            )
        )
        tracker = result.scalars().first()

        if not tracker:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Trigger analysis as a background task
        analyze_daily_tracker.delay(tracker_id, user_id)

        return DailyTrackerResponse.model_validate(tracker)
