from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from auth_service.api.v1.tracker.tracker_schemas import TrackerCreate, TrackerUpdate, TrackerResponse
from libs import ErrorCode, ExceptionBase
from libs.models.body_tracker import BodyTracker


class TrackerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_tracker(self, user_id: int, tracker_data: TrackerCreate) -> TrackerResponse:
        """Create a new tracker record for a user"""
        new_tracker = BodyTracker(user_id=user_id, data=tracker_data.data)
        self.db.add(new_tracker)
        await self.db.commit()
        await self.db.refresh(new_tracker)

        return TrackerResponse.model_validate(new_tracker)

    async def get_tracker(self, tracker_id: int, user_id: int) -> Optional[TrackerResponse]:
        """Get a specific tracker record by ID, ensuring it belongs to the user"""
        result = await self.db.execute(
            select(BodyTracker).where(
                BodyTracker.id == tracker_id, BodyTracker.user_id == user_id, BodyTracker.deleted_date.is_(None)
            )
        )
        tracker = result.scalars().first()

        if not tracker:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return TrackerResponse.model_validate(tracker)

    async def get_tracker_by_user_id(self, user_id: int) -> Optional[TrackerResponse]:
        """Get a user's tracker record by user ID"""
        result = await self.db.execute(
            select(BodyTracker).where(BodyTracker.user_id == user_id, BodyTracker.deleted_date.is_(None))
        )
        tracker = result.scalars().first()

        if not tracker:
            return None

        return TrackerResponse.model_validate(tracker)

    async def list_trackers(self, user_id: int, skip: int = 0, limit: int = 100) -> tuple[List[TrackerResponse], int]:
        """List all tracker records for a user with pagination"""
        # Get total count
        count_query = select(BodyTracker).where(BodyTracker.user_id == user_id, BodyTracker.deleted_date.is_(None))
        count_result = await self.db.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records
        result = await self.db.execute(
            select(BodyTracker)
            .where(BodyTracker.user_id == user_id, BodyTracker.deleted_date.is_(None))
            .offset(skip)
            .limit(limit)
        )
        trackers = result.scalars().all()

        return [TrackerResponse.model_validate(tracker) for tracker in trackers], total_count

    async def update_tracker(self, tracker_id: int, user_id: int, tracker_data: TrackerUpdate) -> TrackerResponse:
        """Update a specific tracker record"""
        # Get the tracker record
        result = await self.db.execute(
            select(BodyTracker).where(
                BodyTracker.id == tracker_id, BodyTracker.user_id == user_id, BodyTracker.deleted_date.is_(None)
            )
        )
        tracker = result.scalars().first()

        if not tracker:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update tracker data
        tracker.data = tracker_data.data
        await self.db.commit()
        await self.db.refresh(tracker)

        return TrackerResponse.model_validate(tracker)

    async def delete_tracker(self, tracker_id: int, user_id: int) -> None:
        """Soft delete a specific tracker record by setting deleted_date"""
        # Verify the tracker exists and belongs to the user
        result = await self.db.execute(
            select(BodyTracker).where(
                BodyTracker.id == tracker_id, BodyTracker.user_id == user_id, BodyTracker.deleted_date.is_(None)
            )
        )
        tracker = result.scalars().first()

        if not tracker:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Soft delete by setting deleted_date
        tracker.deleted_date = datetime.now()
        await self.db.commit()
