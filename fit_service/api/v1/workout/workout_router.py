from fastapi import APIRouter, Depends, Query, status, Header, Path
from typing import Annotated, Optional

from fit_service.api.v1.workout.workout_schemas import (
    WorkoutCategoryCreate,
    WorkoutCategoryUpdate,
    WorkoutCategoryResponse,
    WorkoutCategoryListResponse,
    WorkoutCreate,
    WorkoutUpdate,
    WorkoutResponse,
    WorkoutListResponse,
    WorkoutSetCreate,
    WorkoutSetUpdate,
    WorkoutSetResponse,
    WorkoutProgramCreate,
    WorkoutProgramUpdate,
    WorkoutProgramResponse,
    WorkoutProgramListResponse,
    WorkoutProgramDayCreate,
    WorkoutProgramDayUpdate,
    WorkoutProgramDayResponse,
)
from fit_service.core.services.workout_service import WorkoutService
from sqlalchemy.ext.asyncio import AsyncSession
from libs.db import get_async_db
from libs.service.auth import AuthService
from libs import ErrorCode, ExceptionBase

router = APIRouter(tags=["Workout"], prefix="/workout")


def get_workout_service(db: AsyncSession = Depends(get_async_db)) -> WorkoutService:
    return WorkoutService(db)


def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


# ===== Workout Category Routes =====
@router.post("/categories", response_model=WorkoutCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_workout_category(
    category_data: WorkoutCategoryCreate,
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Create a new workout category (admin only)"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        if user.role != "admin":
            raise ExceptionBase(ErrorCode.FORBIDDEN)
        return await workout_service.create_workout_category(category_data)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.get("/categories/{category_id}", response_model=WorkoutCategoryResponse)
async def get_workout_category(
    category_id: int = Path(..., description="The ID of the workout category"),
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get a specific workout category by ID"""
    await auth_service.get_user_from_token(authorization)
    return await workout_service.get_workout_category(category_id)


@router.get("/categories", response_model=WorkoutCategoryListResponse)
async def list_workout_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """List all workout categories with pagination"""
    await auth_service.get_user_from_token(authorization)
    categories, total_count = await workout_service.list_workout_categories(skip, limit)
    return WorkoutCategoryListResponse(
        items=categories,
        total=total_count,
    )


@router.put("/categories/{category_id}", response_model=WorkoutCategoryResponse)
async def update_workout_category(
    category_id: int,
    category_data: WorkoutCategoryUpdate,
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update a specific workout category (admin only)"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        if user.role != "admin":
            raise ExceptionBase(ErrorCode.FORBIDDEN)
        return await workout_service.update_workout_category(category_id, category_data)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout_category(
    category_id: int,
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Delete a specific workout category (admin only)"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        if user.role != "admin":
            raise ExceptionBase(ErrorCode.FORBIDDEN)
        await workout_service.delete_workout_category(category_id)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


# ===== Workout Program Routes =====
@router.post("/programs", response_model=WorkoutProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_workout_program(
    program_data: WorkoutProgramCreate,
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Create a new workout program with optional days and workouts"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await workout_service.create_workout_program(user.id, program_data)
    except Exception:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.get("/programs/{program_id}", response_model=WorkoutProgramResponse)
async def get_workout_program(
    program_id: int = Path(..., description="The ID of the workout program"),
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get a specific workout program by ID with its days and workouts"""
    user = await auth_service.get_user_from_token(authorization)
    return await workout_service.get_workout_program(program_id, user.id)


@router.get("/programs", response_model=WorkoutProgramListResponse)
async def list_workout_programs(
    group_name: Optional[str] = Query(None, description="Filter by group name"),
    include_public: bool = Query(False, description="Include public programs"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """List workout programs with optional filtering"""
    user = await auth_service.get_user_from_token(authorization)
    programs, total_count = await workout_service.list_workout_programs(
        user_id=user.id, group_name=group_name, include_public=include_public, skip=skip, limit=limit
    )
    return WorkoutProgramListResponse(
        items=programs,
        total=total_count,
    )


@router.put("/programs/{program_id}", response_model=WorkoutProgramResponse)
async def update_workout_program(
    program_id: int,
    program_data: WorkoutProgramUpdate,
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update a specific workout program"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await workout_service.update_workout_program(program_id, user.id, program_data)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.delete("/programs/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout_program(
    program_id: int,
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Delete a specific workout program"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        await workout_service.delete_workout_program(program_id, user.id)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


# ===== Workout Program Day Routes =====
@router.post(
    "/programs/{program_id}/days", response_model=WorkoutProgramDayResponse, status_code=status.HTTP_201_CREATED
)
async def create_workout_program_day(
    program_id: int,
    day_data: WorkoutProgramDayCreate,
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Create a new day for a specific workout program"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await workout_service.create_workout_program_day(program_id, user.id, day_data)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.put("/programs/days/{day_id}", response_model=WorkoutProgramDayResponse)
async def update_workout_program_day(
    day_id: int,
    day_data: WorkoutProgramDayUpdate,
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update a specific workout program day"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await workout_service.update_workout_program_day(day_id, user.id, day_data)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.delete("/programs/days/{day_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout_program_day(
    day_id: int,
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Delete a specific workout program day"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        await workout_service.delete_workout_program_day(day_id, user.id)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


# ===== Workout Routes =====
@router.post("", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
async def create_workout(
    workout_data: WorkoutCreate,
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Create a new workout with optional sets"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await workout_service.create_workout(user.id, workout_data)
    except Exception:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    workout_id: int = Path(..., description="The ID of the workout"),
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get a specific workout by ID with its sets and category"""
    await auth_service.get_user_from_token(authorization)
    return await workout_service.get_workout(workout_id)


@router.get("", response_model=WorkoutListResponse)
async def list_workouts(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """List workouts with optional filtering"""
    user = await auth_service.get_user_from_token(authorization)
    workouts, total_count = await workout_service.list_workouts(
        user_id=user.id, category_id=category_id, difficulty_level=difficulty_level, skip=skip, limit=limit
    )
    return WorkoutListResponse(
        items=workouts,
        total=total_count,
    )


@router.put("/{workout_id}", response_model=WorkoutResponse)
async def update_workout(
    workout_id: int,
    workout_data: WorkoutUpdate,
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update a specific workout"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await workout_service.update_workout(workout_id, user.id, workout_data)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    workout_id: int,
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Delete a specific workout"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        await workout_service.delete_workout(workout_id, user.id)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


# ===== Workout Set Routes =====
@router.post("/{workout_id}/sets", response_model=WorkoutSetResponse, status_code=status.HTTP_201_CREATED)
async def create_workout_set(
    workout_id: int,
    set_data: WorkoutSetCreate,
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Create a new set for a specific workout"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await workout_service.create_workout_set(workout_id, user.id, set_data)
    except Exception:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.put("/sets/{set_id}", response_model=WorkoutSetResponse)
async def update_workout_set(
    set_id: int,
    set_data: WorkoutSetUpdate,
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update a specific workout set"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await workout_service.update_workout_set(set_id, user.id, set_data)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.delete("/sets/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout_set(
    set_id: int,
    authorization: Annotated[str | None, Header()] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Delete a specific workout set"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        await workout_service.delete_workout_set(set_id, user.id)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)
