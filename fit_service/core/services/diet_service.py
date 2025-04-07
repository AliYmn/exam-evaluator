from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from fit_service.api.v1.diet.diet_schemas import DietCreate, DietUpdate, DietResponse, DietTrackerResponse
from libs import ErrorCode, ExceptionBase
from libs.models.diet import Diet
from libs.models.diet_tracker import DietTracker


class DietService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_diet(self, user_id: int, diet_data: DietCreate) -> DietResponse:
        """Create a new diet record for a user"""
        new_diet = Diet(user_id=user_id, data=diet_data.data)
        self.db.add(new_diet)
        await self.db.commit()
        await self.db.refresh(new_diet)

        return DietResponse.model_validate(new_diet)

    async def get_diet(self, diet_id: int, user_id: int) -> Optional[DietResponse]:
        """Get a specific diet record by ID, ensuring it belongs to the user"""
        result = await self.db.execute(
            select(Diet).where(Diet.id == diet_id, Diet.user_id == user_id, Diet.deleted_date.is_(None))
        )
        diet = result.scalars().first()

        if not diet:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return DietResponse.model_validate(diet)

    async def get_diet_by_user_id(self, user_id: int) -> Optional[DietResponse]:
        """Get a user's diet record by user ID"""
        result = await self.db.execute(select(Diet).where(Diet.user_id == user_id, Diet.deleted_date.is_(None)))
        diet = result.scalars().first()

        if not diet:
            return None

        return DietResponse.model_validate(diet)

    async def list_diets(self, user_id: int, skip: int = 0, limit: int = 100) -> tuple[List[DietResponse], int]:
        """List all diet records for a user with pagination"""
        # Get total count
        count_query = select(Diet).where(Diet.user_id == user_id, Diet.deleted_date.is_(None))
        count_result = await self.db.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records
        result = await self.db.execute(
            select(Diet).where(Diet.user_id == user_id, Diet.deleted_date.is_(None)).offset(skip).limit(limit)
        )
        diets = result.scalars().all()

        return [DietResponse.model_validate(diet) for diet in diets], total_count

    async def update_diet(self, diet_id: int, user_id: int, diet_data: DietUpdate) -> DietResponse:
        """Update a specific diet record"""
        # Get the diet record
        result = await self.db.execute(
            select(Diet).where(Diet.id == diet_id, Diet.user_id == user_id, Diet.deleted_date.is_(None))
        )
        diet = result.scalars().first()

        if not diet:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update diet data
        diet.data = diet_data.data
        await self.db.commit()
        await self.db.refresh(diet)

        return DietResponse.model_validate(diet)

    async def delete_diet(self, diet_id: int, user_id: int) -> None:
        """Soft delete a specific diet record by setting deleted_date"""
        # Verify the diet exists and belongs to the user
        result = await self.db.execute(
            select(Diet).where(Diet.id == diet_id, Diet.user_id == user_id, Diet.deleted_date.is_(None))
        )
        diet = result.scalars().first()

        if not diet:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Soft delete by setting deleted_date
        diet.deleted_date = datetime.now()
        await self.db.commit()

    async def list_diet_trackers_by_diet_id(
        self, diet_id: int, user_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[DietTrackerResponse], int]:
        """List all diet tracker records for a specific diet with pagination"""
        # Verify diet exists and belongs to user
        diet_result = await self.db.execute(
            select(Diet).where(Diet.id == diet_id, Diet.user_id == user_id, Diet.deleted_date.is_(None))
        )
        diet = diet_result.scalars().first()

        if not diet:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Get total count
        count_query = select(DietTracker).where(
            DietTracker.diet_id == diet_id, DietTracker.user_id == user_id, DietTracker.deleted_date.is_(None)
        )
        count_result = await self.db.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records
        result = await self.db.execute(
            select(DietTracker)
            .where(DietTracker.diet_id == diet_id, DietTracker.user_id == user_id, DietTracker.deleted_date.is_(None))
            .offset(skip)
            .limit(limit)
        )
        trackers = result.scalars().all()

        return [DietTrackerResponse.model_validate(tracker) for tracker in trackers], total_count

    async def list_diet_trackers_by_user_id(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[DietTrackerResponse], int]:
        """List all diet tracker records for a user with pagination"""
        # Get total count
        count_query = select(DietTracker).where(DietTracker.user_id == user_id, DietTracker.deleted_date.is_(None))
        count_result = await self.db.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records
        result = await self.db.execute(
            select(DietTracker)
            .where(DietTracker.user_id == user_id, DietTracker.deleted_date.is_(None))
            .offset(skip)
            .limit(limit)
        )
        trackers = result.scalars().all()

        return [DietTrackerResponse.model_validate(tracker) for tracker in trackers], total_count
