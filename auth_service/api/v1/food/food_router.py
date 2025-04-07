from fastapi import APIRouter, Depends, Query, status
from typing import Optional

from auth_service.api.v1.food.food_schemas import FoodCreate, FoodUpdate, FoodListResponse
from auth_service.core.services.food_service import FoodService
from sqlalchemy.ext.asyncio import AsyncSession
from libs.db import get_async_db

router = APIRouter(tags=["Food"], prefix="/food")


def get_food_service(db: AsyncSession = Depends(get_async_db)) -> FoodService:
    return FoodService(db)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_food(
    food_data: FoodCreate,
    food_service: FoodService = Depends(get_food_service),
):
    """Create a new food record"""
    return await food_service.create_food(food_data)


@router.get("/{food_id}")
async def get_food(
    food_id: int,
    food_service: FoodService = Depends(get_food_service),
):
    """Get a specific food record by ID"""
    return await food_service.get_food(food_id)


@router.get("")
async def list_foods(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    name: Optional[str] = None,
    category: Optional[str] = None,
    food_service: FoodService = Depends(get_food_service),
):
    """List all food records with optional filtering"""
    if name:
        foods, total_count = await food_service.find_foods_by_name(name, skip, limit)
    elif category:
        foods, total_count = await food_service.find_foods_by_category(category, skip, limit)
    else:
        foods, total_count = await food_service.list_foods(skip, limit)

    return FoodListResponse(
        items=foods,
        count=len(foods),
        total=total_count,
    )


@router.put("/{food_id}")
async def update_food(
    food_id: int,
    food_data: FoodUpdate,
    food_service: FoodService = Depends(get_food_service),
):
    """Update a specific food record"""
    return await food_service.update_food(food_id, food_data)


@router.delete("/{food_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_food(
    food_id: int,
    food_service: FoodService = Depends(get_food_service),
):
    """Delete a specific food record"""
    await food_service.delete_food(food_id)
