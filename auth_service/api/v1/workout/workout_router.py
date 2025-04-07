from fastapi import APIRouter, Depends, Query, status
from typing import Optional

from auth_service.api.v1.workout.workout_schemas import WorkoutCreate, WorkoutUpdate, WorkoutListResponse
from auth_service.core.services.workout_service import WorkoutService
from sqlalchemy.ext.asyncio import AsyncSession
from libs.db import get_async_db

router = APIRouter(tags=["Workout"], prefix="/workout")


def get_workout_service(db: AsyncSession = Depends(get_async_db)) -> WorkoutService:
    return WorkoutService(db)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workout(
    workout_data: WorkoutCreate,
    workout_service: WorkoutService = Depends(get_workout_service),
):
    """Create a new workout record"""
    return await workout_service.create_workout(workout_data)


@router.get("/{workout_id}")
async def get_workout(
    workout_id: int,
    workout_service: WorkoutService = Depends(get_workout_service),
):
    """Get a specific workout record by ID"""
    return await workout_service.get_workout(workout_id)


@router.get("")
async def list_workouts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    name: Optional[str] = None,
    workout_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    workout_service: WorkoutService = Depends(get_workout_service),
):
    """List all workout records with optional filtering"""
    if name:
        workouts, total_count = await workout_service.find_workouts_by_name(name, skip, limit)
    elif workout_type:
        workouts, total_count = await workout_service.find_workouts_by_type(workout_type, skip, limit)
    elif difficulty:
        workouts, total_count = await workout_service.find_workouts_by_difficulty(difficulty, skip, limit)
    else:
        workouts, total_count = await workout_service.list_workouts(skip, limit)

    return WorkoutListResponse(
        items=workouts,
        count=len(workouts),
        total=total_count,
    )


@router.put("/{workout_id}")
async def update_workout(
    workout_id: int,
    workout_data: WorkoutUpdate,
    workout_service: WorkoutService = Depends(get_workout_service),
):
    """Update a specific workout record"""
    return await workout_service.update_workout(workout_id, workout_data)


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    workout_id: int,
    workout_service: WorkoutService = Depends(get_workout_service),
):
    """Delete a specific workout record"""
    await workout_service.delete_workout(workout_id)
