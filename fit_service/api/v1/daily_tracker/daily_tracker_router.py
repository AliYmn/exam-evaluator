from fastapi import APIRouter, Depends, Query, status, Header
from typing import Annotated

from fit_service.api.v1.daily_tracker.daily_tracker_schemas import (
    DailyTrackerCreate,
    DailyTrackerUpdate,
    DailyTrackerListResponse,
)
from fit_service.core.services.daily_tracker_service import DailyTrackerService
from sqlalchemy.ext.asyncio import AsyncSession
from libs.db import get_async_db
from libs.service.auth import AuthService
from libs import ErrorCode, ExceptionBase

router = APIRouter(tags=["Daily Tracker"], prefix="/daily-tracker")


def get_daily_tracker_service(db: AsyncSession = Depends(get_async_db)) -> DailyTrackerService:
    return DailyTrackerService(db)


def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_daily_tracker(
    tracker_data: DailyTrackerCreate,
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: DailyTrackerService = Depends(get_daily_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Create a new daily tracker record for the authenticated user"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await tracker_service.create_daily_tracker(user.id, tracker_data)
    except Exception:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.get("/{tracker_id}")
async def get_daily_tracker(
    tracker_id: int,
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: DailyTrackerService = Depends(get_daily_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get a specific daily tracker record by ID"""
    user = await auth_service.get_user_from_token(authorization)
    return await tracker_service.get_daily_tracker(tracker_id, user.id)


@router.get("")
async def list_daily_trackers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: DailyTrackerService = Depends(get_daily_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """List all daily tracker records for the authenticated user"""
    user = await auth_service.get_user_from_token(authorization)
    trackers, total_count = await tracker_service.list_daily_trackers(user.id, skip, limit)
    return DailyTrackerListResponse(
        items=trackers,
        count=len(trackers),
        total=total_count,
    )


@router.get("/latest")
async def get_latest_daily_tracker(
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: DailyTrackerService = Depends(get_daily_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get the latest daily tracker record for the authenticated user"""
    user = await auth_service.get_user_from_token(authorization)
    tracker = await tracker_service.get_latest_daily_tracker(user.id)
    if not tracker:
        raise ExceptionBase(ErrorCode.NOT_FOUND)
    return tracker


@router.put("/{tracker_id}")
async def update_daily_tracker(
    tracker_id: int,
    tracker_data: DailyTrackerUpdate,
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: DailyTrackerService = Depends(get_daily_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update a specific daily tracker record"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await tracker_service.update_daily_tracker(tracker_id, user.id, tracker_data)
    except Exception:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.delete("/{tracker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_daily_tracker(
    tracker_id: int,
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: DailyTrackerService = Depends(get_daily_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Delete a specific daily tracker record"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        await tracker_service.delete_daily_tracker(tracker_id, user.id)
    except Exception:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)
