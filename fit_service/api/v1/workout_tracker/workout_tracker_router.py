from fastapi import APIRouter, Depends, Query, status, Header
from typing import Annotated

from fit_service.api.v1.workout_tracker.workout_tracker_schemas import (
    WorkoutTrackerCreate,
    WorkoutTrackerUpdate,
    WorkoutTrackerListResponse,
)
from fit_service.core.services.workout_tracker_service import WorkoutTrackerService
from sqlalchemy.ext.asyncio import AsyncSession
from libs.db import get_async_db
from libs.service.auth import AuthService
from libs import ErrorCode, ExceptionBase

router = APIRouter(tags=["Workout Tracker"], prefix="/workout-tracker")


def get_workout_tracker_service(db: AsyncSession = Depends(get_async_db)) -> WorkoutTrackerService:
    return WorkoutTrackerService(db)


def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
async def create_workout_tracker(
    tracker_data: WorkoutTrackerCreate,
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: WorkoutTrackerService = Depends(get_workout_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        user = await auth_service.get_user_from_token(authorization)
        await tracker_service.create_workout_tracker(user.id, tracker_data)
    except Exception:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.get("")
async def list_workout_trackers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: WorkoutTrackerService = Depends(get_workout_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    trackers, total_count = await tracker_service.list_workout_trackers(user.id, skip, limit)
    return WorkoutTrackerListResponse(
        items=trackers,
        count=len(trackers),
        total=total_count,
    )


@router.get("/latest")
async def get_latest_workout_tracker(
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: WorkoutTrackerService = Depends(get_workout_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    tracker = await tracker_service.get_latest_workout_tracker(user.id)
    if not tracker:
        raise ExceptionBase(ErrorCode.NOT_FOUND)
    return tracker


@router.get("/{tracker_id}")
async def get_workout_tracker(
    tracker_id: int,
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: WorkoutTrackerService = Depends(get_workout_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    return await tracker_service.get_workout_tracker(tracker_id, user.id)


@router.put("/{tracker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_workout_tracker(
    tracker_id: int,
    tracker_data: WorkoutTrackerUpdate,
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: WorkoutTrackerService = Depends(get_workout_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        user = await auth_service.get_user_from_token(authorization)
        await tracker_service.update_workout_tracker(tracker_id, user.id, tracker_data)
    except Exception:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.delete("/{tracker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout_tracker(
    tracker_id: int,
    authorization: Annotated[str | None, Header()] = None,
    tracker_service: WorkoutTrackerService = Depends(get_workout_tracker_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        user = await auth_service.get_user_from_token(authorization)
        await tracker_service.delete_workout_tracker(tracker_id, user.id)
    except Exception:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)
