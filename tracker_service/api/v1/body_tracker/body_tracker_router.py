from fastapi import APIRouter, Depends, Query, status, Header
from typing import Annotated
from fastapi_limiter.depends import RateLimiter

from tracker_service.api.v1.body_tracker.body_tracker_schemas import (
    TrackerCreate,
    TrackerUpdate,
    TrackerListResponse,
)
from tracker_service.core.services.body_tracker_service import BodyTrackerService
from sqlalchemy.ext.asyncio import AsyncSession
from libs.db import get_async_db
from libs.service.auth import AuthService

router = APIRouter(tags=["Body Tracker"], prefix="/body-tracker")


def get_body_tracker_service(db: AsyncSession = Depends(get_async_db)) -> BodyTrackerService:
    return BodyTrackerService(db)


def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


@router.post("", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RateLimiter(times=15, seconds=60))])
async def create_tracker(
    tracker_data: TrackerCreate,
    authorization: Annotated[str | None, Header()] = None,
    body_tracker_service: BodyTrackerService = Depends(get_body_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Create a new tracker record for the authenticated user"""
    user = await auth_service.get_user_from_token(authorization)
    await body_tracker_service.create_tracker(user.id, tracker_data)


@router.get("/{tracker_id}")
async def get_tracker(
    tracker_id: int,
    authorization: Annotated[str | None, Header()] = None,
    body_tracker_service: BodyTrackerService = Depends(get_body_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get a specific tracker record by ID"""
    user = await auth_service.get_user_from_token(authorization)
    return await body_tracker_service.get_tracker(tracker_id, user.id)


@router.get("", dependencies=[Depends(RateLimiter(times=15, seconds=60))])
async def list_trackers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    body_tracker_service: BodyTrackerService = Depends(get_body_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """List all tracker records for the authenticated user"""
    user = await auth_service.get_user_from_token(authorization)
    trackers, total_count = await body_tracker_service.list_trackers(user.id, skip, limit)
    return TrackerListResponse(
        items=trackers,
        total=total_count,
    )


@router.put("/{tracker_id}")
async def update_tracker(
    tracker_id: int,
    tracker_data: TrackerUpdate,
    authorization: Annotated[str | None, Header()] = None,
    body_tracker_service: BodyTrackerService = Depends(get_body_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update a specific tracker record"""
    user = await auth_service.get_user_from_token(authorization)
    return await body_tracker_service.update_tracker(tracker_id, user.id, tracker_data)


@router.delete("/{tracker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tracker(
    tracker_id: int,
    authorization: Annotated[str | None, Header()] = None,
    body_tracker_service: BodyTrackerService = Depends(get_body_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Delete a specific tracker record"""
    user = await auth_service.get_user_from_token(authorization)
    await body_tracker_service.delete_tracker(tracker_id, user.id)
# Refactored on 2025-09-24: Improved code structure
# Updated on 2025-09-25: Improved code documentation
# Fixed formatting on 2025-09-26
# Refactored on 2025-09-26: Improved code structure
# Fixed formatting on 2025-09-26
# Refactored on 2025-09-27: Improved code structure
# Refactored on 2025-09-27: Improved code structure
# Fixed formatting on 2025-09-28
# Updated on 2025-09-29: Improved code documentation
# Fixed formatting on 2025-09-29
# Refactored on 2025-09-30: Improved code structure
