from fastapi import APIRouter, Depends, Query, status, Header
from typing import Annotated

from fit_service.api.v1.body_tracker.body_tracker_schemas import (
    TrackerCreate,
    TrackerUpdate,
    TrackerListResponse,
)
from fit_service.core.services.tracker_service import TrackerService
from sqlalchemy.ext.asyncio import AsyncSession
from libs.db import get_async_db
from libs.service.auth import AuthService
from libs import ErrorCode, ExceptionBase

router = APIRouter(tags=["Body Tracker"], prefix="/tracker")


def get_tracker_service(db: AsyncSession = Depends(get_async_db)) -> TrackerService:
    return TrackerService(db)


def get_fit_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_tracker(
    tracker_data: TrackerCreate,
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: TrackerService = Depends(get_tracker_service),
    fit_service: AuthService = Depends(get_fit_service),
):
    """Create a new tracker record for the authenticated user"""
    try:
        user = await fit_service.get_user_from_token(authorization)
        return await tracker_service.create_tracker(user.id, tracker_data)
    except Exception:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.get("/{tracker_id}")
async def get_tracker(
    tracker_id: int,
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: TrackerService = Depends(get_tracker_service),
    fit_service: AuthService = Depends(get_fit_service),
):
    """Get a specific tracker record by ID"""
    user = await fit_service.get_user_from_token(authorization)
    return await tracker_service.get_tracker(tracker_id, user.id)


@router.get("")
async def list_trackers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: TrackerService = Depends(get_tracker_service),
    fit_service: AuthService = Depends(get_fit_service),
):
    """List all tracker records for the authenticated user"""
    user = await fit_service.get_user_from_token(authorization)
    trackers, total_count = await tracker_service.list_trackers(user.id, skip, limit)
    return TrackerListResponse(
        items=trackers,
        count=len(trackers),
        total=total_count,
    )


@router.put("/{tracker_id}")
async def update_tracker(
    tracker_id: int,
    tracker_data: TrackerUpdate,
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: TrackerService = Depends(get_tracker_service),
    fit_service: AuthService = Depends(get_fit_service),
):
    """Update a specific tracker record"""
    try:
        user = await fit_service.get_user_from_token(authorization)
        return await tracker_service.update_tracker(tracker_id, user.id, tracker_data)
    except Exception:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.delete("/{tracker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tracker(
    tracker_id: int,
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: TrackerService = Depends(get_tracker_service),
    fit_service: AuthService = Depends(get_fit_service),
):
    """Delete a specific tracker record"""
    try:
        user = await fit_service.get_user_from_token(authorization)
        await tracker_service.delete_tracker(tracker_id, user.id)
    except Exception:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)
