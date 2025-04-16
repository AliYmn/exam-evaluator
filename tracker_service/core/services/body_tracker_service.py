from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracker_service.api.v1.body_tracker.body_tracker_schemas import TrackerCreate, TrackerUpdate, TrackerResponse
from libs import ErrorCode, ExceptionBase
from libs.models.body_tracker import BodyTracker
from tracker_service.core.worker.tasks import analyze_body_tracker


class BodyTrackerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_tracker(self, user_id: int, tracker_data: TrackerCreate) -> TrackerResponse:
        """Create a new tracker record for a user"""
        new_tracker = BodyTracker(
            user_id=user_id,
            weight=tracker_data.weight,
            neck=tracker_data.neck,
            waist=tracker_data.waist,
            shoulder=tracker_data.shoulder,
            chest=tracker_data.chest,
            hip=tracker_data.hip,
            thigh=tracker_data.thigh,
            arm=tracker_data.arm,
        )
        self.db.add(new_tracker)
        await self.db.commit()
        await self.db.refresh(new_tracker)

        # Trigger analysis as a background task
        analyze_body_tracker.delay(new_tracker.id, user_id)

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

    async def list_trackers(self, user_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[TrackerResponse], int]:
        """List all tracker records for a user with pagination"""
        # Get total count
        count_query = select(BodyTracker).where(BodyTracker.user_id == user_id, BodyTracker.deleted_date.is_(None))
        count_result = await self.db.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records
        result = await self.db.execute(
            select(BodyTracker)
            .where(BodyTracker.user_id == user_id, BodyTracker.deleted_date.is_(None))
            .order_by(BodyTracker.created_date.desc())
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

        # Update fields if provided
        if tracker_data.weight is not None:
            tracker.weight = tracker_data.weight
        if tracker_data.neck is not None:
            tracker.neck = tracker_data.neck
        if tracker_data.waist is not None:
            tracker.waist = tracker_data.waist
        if tracker_data.shoulder is not None:
            tracker.shoulder = tracker_data.shoulder
        if tracker_data.chest is not None:
            tracker.chest = tracker_data.chest
        if tracker_data.hip is not None:
            tracker.hip = tracker_data.hip
        if tracker_data.thigh is not None:
            tracker.thigh = tracker_data.thigh
        if tracker_data.arm is not None:
            tracker.arm = tracker_data.arm

        # Save changes
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

        # Soft delete
        tracker.soft_delete()
        await self.db.commit()

    async def analyze_tracker(self, tracker_id: int, user_id: int) -> Optional[TrackerResponse]:
        """Analyze a specific tracker record and update its AI content"""
        # First verify the tracker exists and belongs to the user
        result = await self.db.execute(
            select(BodyTracker).where(
                BodyTracker.id == tracker_id, BodyTracker.user_id == user_id, BodyTracker.deleted_date.is_(None)
            )
        )
        tracker = result.scalars().first()

        if not tracker:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Trigger analysis as a background task
        analyze_body_tracker.delay(tracker_id, user_id)

        return TrackerResponse.model_validate(tracker)
