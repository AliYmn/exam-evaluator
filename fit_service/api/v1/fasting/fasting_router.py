from fastapi import APIRouter, Depends, Query, status, Header, HTTPException
from typing import Annotated
from fastapi_limiter.depends import RateLimiter

from fit_service.api.v1.fasting.fasting_schemas import (
    FastingPlanCreate,
    FastingPlanUpdate,
    FastingPlanListResponse,
    FastingSessionCreate,
    FastingSessionUpdate,
    FastingSessionListResponse,
    FastingMealLogCreate,
    FastingMealLogUpdate,
    FastingMealLogListResponse,
    FastingWorkoutLogCreate,
    FastingWorkoutLogUpdate,
    FastingWorkoutLogListResponse,
)
from fit_service.core.services.fasting_service import FastingService
from sqlalchemy.ext.asyncio import AsyncSession
from libs.db import get_async_db
from libs.service.auth import AuthService

router = APIRouter(tags=["Fasting"], prefix="/fasting")


def get_fasting_service(db: AsyncSession = Depends(get_async_db)) -> FastingService:
    return FastingService(db)


def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


# FastingPlan endpoints
@router.post("/plans", status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=15, seconds=60))])
async def create_fasting_plan(
    plan_data: FastingPlanCreate,
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    return await fasting_service.create_fasting_plan(user.id, plan_data)


@router.get("/plans")
async def list_fasting_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    plans, total_count = await fasting_service.list_fasting_plans(user.id, skip, limit)
    return FastingPlanListResponse(
        items=plans,
        count=len(plans),
        total=total_count,
    )


@router.get("/plans/active")
async def get_active_fasting_plan(
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    plan = await fasting_service.get_active_fasting_plan(user.id)
    if not plan:
        raise HTTPException(status_code=404, detail="No active fasting plan found")
    return plan


@router.get("/plans/{plan_id}")
async def get_fasting_plan(
    plan_id: int,
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    return await fasting_service.get_fasting_plan(plan_id, user.id)


@router.put("/plans/{plan_id}")
async def update_fasting_plan(
    plan_id: int,
    plan_data: FastingPlanUpdate,
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    return await fasting_service.update_fasting_plan(plan_id, user.id, plan_data)


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fasting_plan(
    plan_id: int,
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    await fasting_service.delete_fasting_plan(plan_id, user.id)


# FastingSession endpoints
@router.post(
    "/sessions", status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=15, seconds=60))]
)
async def create_fasting_session(
    session_data: FastingSessionCreate,
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    return await fasting_service.create_fasting_session(user.id, session_data)


@router.get("/sessions")
async def list_fasting_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    sessions, total_count = await fasting_service.list_fasting_sessions(user.id, skip, limit)
    return FastingSessionListResponse(
        items=sessions,
        count=len(sessions),
        total=total_count,
    )


@router.get("/sessions/latest")
async def get_latest_fasting_session(
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    session = await fasting_service.get_latest_fasting_session(user.id)
    if not session:
        raise HTTPException(status_code=404, detail="No fasting sessions found")
    return session


@router.get("/sessions/{session_id}")
async def get_fasting_session(
    session_id: int,
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    return await fasting_service.get_fasting_session(session_id, user.id)


@router.put("/sessions/{session_id}")
async def update_fasting_session(
    session_id: int,
    session_data: FastingSessionUpdate,
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    return await fasting_service.update_fasting_session(session_id, user.id, session_data)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fasting_session(
    session_id: int,
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    await fasting_service.delete_fasting_session(session_id, user.id)


# FastingMealLog endpoints
@router.post(
    "/meal-logs", status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=15, seconds=60))]
)
async def create_meal_log(
    meal_data: FastingMealLogCreate,
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    return await fasting_service.create_meal_log(user.id, meal_data)


@router.get("/meal-logs/{log_id}")
async def get_meal_log(
    log_id: int,
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    return await fasting_service.get_meal_log(log_id, user.id)


@router.get("/meal-logs")
async def list_meal_logs(
    session_id: int = Query(None, description="Filter logs by session ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    logs, total_count = await fasting_service.list_meal_logs(user.id, session_id, skip, limit)
    return FastingMealLogListResponse(
        items=logs,
        count=len(logs),
        total=total_count,
    )


@router.put("/meal-logs/{log_id}")
async def update_meal_log(
    log_id: int,
    meal_data: FastingMealLogUpdate,
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    return await fasting_service.update_meal_log(log_id, user.id, meal_data)


@router.delete("/meal-logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal_log(
    log_id: int,
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    await fasting_service.delete_meal_log(log_id, user.id)


# FastingWorkoutLog endpoints
@router.post(
    "/workout-logs", status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=15, seconds=60))]
)
async def create_workout_log(
    workout_data: FastingWorkoutLogCreate,
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    return await fasting_service.create_workout_log(user.id, workout_data)


@router.get("/workout-logs/{log_id}")
async def get_workout_log(
    log_id: int,
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    return await fasting_service.get_workout_log(log_id, user.id)


@router.get("/workout-logs")
async def list_workout_logs(
    session_id: int = Query(None, description="Filter logs by session ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    logs, total_count = await fasting_service.list_workout_logs(user.id, session_id, skip, limit)
    return FastingWorkoutLogListResponse(
        items=logs,
        count=len(logs),
        total=total_count,
    )


@router.put("/workout-logs/{log_id}")
async def update_workout_log(
    log_id: int,
    workout_data: FastingWorkoutLogUpdate,
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    return await fasting_service.update_workout_log(log_id, user.id, workout_data)


@router.delete("/workout-logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout_log(
    log_id: int,
    authorization: Annotated[str | None, Header()] = None,
    fasting_service: FastingService = Depends(get_fasting_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_from_token(authorization)
    await fasting_service.delete_workout_log(log_id, user.id)
