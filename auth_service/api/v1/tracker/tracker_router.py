from fastapi import APIRouter, Depends, Query, status, Header
from typing import Annotated

from auth_service.api.v1.tracker.tracker_schemas import (
    TrackerCreate,
    TrackerUpdate,
    TrackerResponse,
    TrackerListResponse,
)
from auth_service.core.services.tracker_service import TrackerService
from libs.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from libs.db import get_async_db
from libs.service.auth import AuthService
from libs import ErrorCode, ExceptionBase

router = APIRouter(tags=["tracker"], prefix="/tracker")


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_async_db),
) -> User:
    """Validates the user's token and returns the current user"""
    if not authorization:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)

    auth_service = AuthService(db)
    try:
        _, user = await auth_service.validate_token(authorization)
        if not user:
            raise ExceptionBase(ErrorCode.NOT_FOUND)
        return user
    except Exception as e:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED, str(e))


@router.post("", response_model=TrackerResponse, status_code=status.HTTP_201_CREATED)
async def create_tracker(
    tracker_data: TrackerCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new tracker record for the authenticated user"""
    tracker_service = TrackerService(db)
    return await tracker_service.create_tracker(user.id, tracker_data)


@router.get("/{tracker_id}", response_model=TrackerResponse)
async def get_tracker(
    tracker_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Get a specific tracker record by ID"""
    tracker_service = TrackerService(db)
    return await tracker_service.get_tracker(tracker_id, user.id)


@router.get("", response_model=TrackerListResponse)
async def list_trackers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """List all tracker records for the authenticated user"""
    tracker_service = TrackerService(db)
    trackers, total_count = await tracker_service.list_trackers(user.id, skip, limit)

    return TrackerListResponse(
        items=trackers,
        count=len(trackers),
        total=total_count,
    )


@router.put("/{tracker_id}", response_model=TrackerResponse)
async def update_tracker(
    tracker_id: int,
    tracker_data: TrackerUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Update a specific tracker record"""
    tracker_service = TrackerService(db)
    return await tracker_service.update_tracker(tracker_id, user.id, tracker_data)


@router.delete("/{tracker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tracker(
    tracker_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Delete a specific tracker record"""
    tracker_service = TrackerService(db)
    await tracker_service.delete_tracker(tracker_id, user.id)
    return None
