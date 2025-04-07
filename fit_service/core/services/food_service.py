from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from fit_service.api.v1.food.food_schemas import FoodCreate, FoodUpdate, FoodResponse
from libs import ErrorCode, ExceptionBase
from libs.models.food import Food


class FoodService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_food(self, food_data: FoodCreate) -> FoodResponse:
        """Create a new food record"""
        new_food = Food(
            name=food_data.name,
            description=food_data.description,
            category=food_data.category,
            calories=food_data.calories,
            protein=food_data.protein,
            carbs=food_data.carbs,
            fat=food_data.fat,
            fiber=food_data.fiber,
            sugar=food_data.sugar,
            extra=food_data.extra,
        )
        self.db.add(new_food)
        await self.db.commit()
        await self.db.refresh(new_food)

        return FoodResponse.model_validate(new_food)

    async def get_food(self, food_id: int) -> Optional[FoodResponse]:
        """Get a specific food record by ID"""
        result = await self.db.execute(select(Food).where(Food.id == food_id, Food.deleted_date.is_(None)))
        food = result.scalars().first()

        if not food:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return FoodResponse.model_validate(food)

    async def list_foods(self, skip: int = 0, limit: int = 100) -> tuple[List[FoodResponse], int]:
        """List all food records with pagination"""
        # Get total count
        count_query = select(Food).where(Food.deleted_date.is_(None))
        count_result = await self.db.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records
        result = await self.db.execute(select(Food).where(Food.deleted_date.is_(None)).offset(skip).limit(limit))
        foods = result.scalars().all()

        return [FoodResponse.model_validate(food) for food in foods], total_count

    async def update_food(self, food_id: int, food_data: FoodUpdate) -> FoodResponse:
        """Update a specific food record"""
        # Get the food record
        result = await self.db.execute(select(Food).where(Food.id == food_id, Food.deleted_date.is_(None)))
        food = result.scalars().first()

        if not food:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update food data
        if food_data.name is not None:
            food.name = food_data.name
        if food_data.description is not None:
            food.description = food_data.description
        if food_data.category is not None:
            food.category = food_data.category
        if food_data.calories is not None:
            food.calories = food_data.calories
        if food_data.protein is not None:
            food.protein = food_data.protein
        if food_data.carbs is not None:
            food.carbs = food_data.carbs
        if food_data.fat is not None:
            food.fat = food_data.fat
        if food_data.fiber is not None:
            food.fiber = food_data.fiber
        if food_data.sugar is not None:
            food.sugar = food_data.sugar
        if food_data.extra:
            food.extra = food_data.extra

        await self.db.commit()
        await self.db.refresh(food)

        return FoodResponse.model_validate(food)

    async def delete_food(self, food_id: int) -> None:
        """Soft delete a specific food record by setting deleted_date"""
        # Verify the food exists
        result = await self.db.execute(select(Food).where(Food.id == food_id, Food.deleted_date.is_(None)))
        food = result.scalars().first()

        if not food:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Soft delete by setting deleted_date
        food.deleted_date = datetime.now()
        await self.db.commit()

    async def find_foods_by_name(self, name: str, skip: int = 0, limit: int = 100) -> tuple[List[FoodResponse], int]:
        """Find foods by name (partial match)"""
        search_term = f"%{name}%"

        # Get total count
        count_query = select(Food).where(Food.name.ilike(search_term), Food.deleted_date.is_(None))
        count_result = await self.db.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records
        result = await self.db.execute(
            select(Food).where(Food.name.ilike(search_term), Food.deleted_date.is_(None)).offset(skip).limit(limit)
        )
        foods = result.scalars().all()

        return [FoodResponse.model_validate(food) for food in foods], total_count

    async def find_foods_by_category(
        self, category: str, skip: int = 0, limit: int = 100
    ) -> tuple[List[FoodResponse], int]:
        """Find foods by category"""
        # Get total count
        count_query = select(Food).where(Food.category == category, Food.deleted_date.is_(None))
        count_result = await self.db.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records
        result = await self.db.execute(
            select(Food).where(Food.category == category, Food.deleted_date.is_(None)).offset(skip).limit(limit)
        )
        foods = result.scalars().all()

        return [FoodResponse.model_validate(food) for food in foods], total_count
