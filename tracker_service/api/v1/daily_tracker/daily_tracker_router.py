from fastapi import APIRouter, Depends, Query, status, Header, HTTPException
from typing import Annotated

from tracker_service.api.v1.daily_tracker.daily_tracker_schemas import (
    DailyTrackerCreate,
    DailyTrackerUpdate,
    DailyTrackerListResponse,
)
from tracker_service.core.services.daily_tracker_service import DailyTrackerService
from sqlalchemy.ext.asyncio import AsyncSession
from libs.db import get_async_db
from libs.service.auth import AuthService

router = APIRouter(tags=["Daily Tracker"], prefix="/daily-tracker")


def get_daily_tracker_service(db: AsyncSession = Depends(get_async_db)) -> DailyTrackerService:
    return DailyTrackerService(db)


def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
async def create_daily_tracker(
    tracker_data: DailyTrackerCreate,
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: DailyTrackerService = Depends(get_daily_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    await tracker_service.create_daily_tracker(user.id, tracker_data)


@router.get("")
async def list_daily_trackers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: DailyTrackerService = Depends(get_daily_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
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
    user = await auth_service.get_user_from_token(authorization)
    tracker = await tracker_service.get_latest_daily_tracker(user.id)
    if not tracker:
        raise HTTPException(status_code=404, detail="Daily tracker not found")
    return tracker


@router.get("/{tracker_id}")
async def get_daily_tracker(
    tracker_id: int,
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: DailyTrackerService = Depends(get_daily_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    return await tracker_service.get_daily_tracker(tracker_id, user.id)


@router.put("/{tracker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_daily_tracker(
    tracker_id: int,
    tracker_data: DailyTrackerUpdate,
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: DailyTrackerService = Depends(get_daily_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    await tracker_service.update_daily_tracker(tracker_id, user.id, tracker_data)


@router.delete("/{tracker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_daily_tracker(
    tracker_id: int,
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: DailyTrackerService = Depends(get_daily_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    await tracker_service.delete_daily_tracker(tracker_id, user.id)
