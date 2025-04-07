from typing import List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fit_service.api.v1.diet.diet_schemas import (
    FoodCategoryCreate,
    FoodCategoryUpdate,
    FoodCategoryResponse,
    FoodCreate,
    FoodUpdate,
    FoodResponse,
    SupplementCategoryCreate,
    SupplementCategoryUpdate,
    SupplementCategoryResponse,
    SupplementCreate,
    SupplementUpdate,
    SupplementResponse,
    DietPlanCreate,
    DietPlanUpdate,
    DietPlanResponse,
    MealTemplateCreate,
    MealTemplateUpdate,
    MealTemplateResponse,
)
from libs import ErrorCode, ExceptionBase
from libs.models.diet import (
    FoodCategory,
    Food,
    SupplementCategory,
    Supplement,
    DietPlan,
    diet_plan_food,
    diet_plan_supplement,
    MealTemplate,
    MealTemplateFood,
)


class DietService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ===== Food Category Methods =====
    async def create_food_category(self, category_data: FoodCategoryCreate) -> FoodCategoryResponse:
        """Create a new food category"""
        new_category = FoodCategory(
            name=category_data.name,
            description=category_data.description,
        )
        self.db.add(new_category)
        await self.db.commit()
        await self.db.refresh(new_category)

        return FoodCategoryResponse.model_validate(new_category)

    async def get_food_category(self, category_id: int) -> FoodCategoryResponse:
        """Get a specific food category by ID"""
        result = await self.db.execute(
            select(FoodCategory).where(FoodCategory.id == category_id, FoodCategory.deleted_date.is_(None))
        )
        category = result.scalars().first()
        if not category:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return FoodCategoryResponse.model_validate(category)

    async def list_food_categories(self, skip: int = 0, limit: int = 100) -> Tuple[List[FoodCategoryResponse], int]:
        """List all food categories with pagination"""
        # Get total count
        count_query = select(FoodCategory).where(FoodCategory.deleted_date.is_(None))
        count_result = await self.db.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records
        result = await self.db.execute(
            select(FoodCategory)
            .where(FoodCategory.deleted_date.is_(None))
            .order_by(FoodCategory.name)
            .offset(skip)
            .limit(limit)
        )
        categories = result.scalars().all()

        return [FoodCategoryResponse.model_validate(category) for category in categories], total_count

    async def update_food_category(self, category_id: int, category_data: FoodCategoryUpdate) -> FoodCategoryResponse:
        """Update a specific food category"""
        result = await self.db.execute(
            select(FoodCategory).where(FoodCategory.id == category_id, FoodCategory.deleted_date.is_(None))
        )
        category = result.scalars().first()
        if not category:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update fields if provided
        if category_data.name is not None:
            category.name = category_data.name
        if category_data.description is not None:
            category.description = category_data.description

        await self.db.commit()
        await self.db.refresh(category)

        return FoodCategoryResponse.model_validate(category)

    async def delete_food_category(self, category_id: int) -> None:
        """Soft delete a specific food category"""
        result = await self.db.execute(
            select(FoodCategory).where(FoodCategory.id == category_id, FoodCategory.deleted_date.is_(None))
        )
        category = result.scalars().first()
        if not category:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        category.soft_delete()
        await self.db.commit()

    # ===== Food Methods =====
    async def create_food(self, user_id: int, food_data: FoodCreate) -> FoodResponse:
        """Create a new food"""
        new_food = Food(
            name=food_data.name,
            description=food_data.description,
            category_id=food_data.category_id,
            calories=food_data.calories,
            protein=food_data.protein,
            carbs=food_data.carbs,
            fat=food_data.fat,
            fiber=food_data.fiber,
            sugar=food_data.sugar,
            serving_size=food_data.serving_size,
            serving_unit=food_data.serving_unit,
            image_url=food_data.image_url,
            user_id=user_id,
            is_custom=food_data.is_custom,
        )
        self.db.add(new_food)
        await self.db.commit()
        await self.db.refresh(new_food)

        # Load the food with relationships for response
        result = await self.db.execute(select(Food).options(joinedload(Food.category)).where(Food.id == new_food.id))
        food_with_relations = result.scalars().first()

        return FoodResponse.model_validate(food_with_relations)

    async def get_food(self, food_id: int) -> FoodResponse:
        """Get a specific food by ID with its category"""
        result = await self.db.execute(
            select(Food).options(joinedload(Food.category)).where(Food.id == food_id, Food.deleted_date.is_(None))
        )
        food = result.scalars().first()
        if not food:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return FoodResponse.model_validate(food)

    async def list_foods(
        self, user_id: Optional[int] = None, category_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> Tuple[List[FoodResponse], int]:
        """List foods with optional filtering by user_id and category_id"""
        # Build base query
        base_query = select(Food).where(Food.deleted_date.is_(None))

        # Apply filters
        if user_id is not None:
            base_query = base_query.where((Food.user_id == user_id) | (Food.is_custom == 0))
        if category_id is not None:
            base_query = base_query.where(Food.category_id == category_id)

        # Get total count
        count_result = await self.db.execute(base_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records with relationships
        result = await self.db.execute(
            base_query.options(joinedload(Food.category)).order_by(Food.name).offset(skip).limit(limit)
        )
        foods = result.scalars().all()

        return [FoodResponse.model_validate(food) for food in foods], total_count

    async def update_food(self, food_id: int, user_id: int, food_data: FoodUpdate) -> FoodResponse:
        """Update a specific food"""
        # Get the food with ownership check
        result = await self.db.execute(
            select(Food).where(Food.id == food_id, Food.user_id == user_id, Food.deleted_date.is_(None))
        )
        food = result.scalars().first()
        if not food:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update fields if provided
        if food_data.name is not None:
            food.name = food_data.name
        if food_data.description is not None:
            food.description = food_data.description
        if food_data.category_id is not None:
            food.category_id = food_data.category_id
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
        if food_data.serving_size is not None:
            food.serving_size = food_data.serving_size
        if food_data.serving_unit is not None:
            food.serving_unit = food_data.serving_unit
        if food_data.image_url is not None:
            food.image_url = food_data.image_url
        if food_data.is_custom is not None:
            food.is_custom = food_data.is_custom

        await self.db.commit()

        # Load the food with relationships for response
        result = await self.db.execute(select(Food).options(joinedload(Food.category)).where(Food.id == food_id))
        updated_food = result.scalars().first()

        return FoodResponse.model_validate(updated_food)

    async def delete_food(self, food_id: int, user_id: int) -> None:
        """Soft delete a specific food with ownership check"""
        result = await self.db.execute(
            select(Food).where(Food.id == food_id, Food.user_id == user_id, Food.deleted_date.is_(None))
        )
        food = result.scalars().first()
        if not food:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        food.soft_delete()
        await self.db.commit()

    # ===== Supplement Category Methods =====
    async def create_supplement_category(self, category_data: SupplementCategoryCreate) -> SupplementCategoryResponse:
        """Create a new supplement category"""
        new_category = SupplementCategory(
            name=category_data.name,
            description=category_data.description,
        )
        self.db.add(new_category)
        await self.db.commit()
        await self.db.refresh(new_category)

        return SupplementCategoryResponse.model_validate(new_category)

    async def get_supplement_category(self, category_id: int) -> SupplementCategoryResponse:
        """Get a specific supplement category by ID"""
        result = await self.db.execute(
            select(SupplementCategory).where(
                SupplementCategory.id == category_id, SupplementCategory.deleted_date.is_(None)
            )
        )
        category = result.scalars().first()
        if not category:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return SupplementCategoryResponse.model_validate(category)

    async def list_supplement_categories(
        self, skip: int = 0, limit: int = 100
    ) -> Tuple[List[SupplementCategoryResponse], int]:
        """List all supplement categories with pagination"""
        # Get total count
        count_query = select(SupplementCategory).where(SupplementCategory.deleted_date.is_(None))
        count_result = await self.db.execute(count_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records
        result = await self.db.execute(
            select(SupplementCategory)
            .where(SupplementCategory.deleted_date.is_(None))
            .order_by(SupplementCategory.name)
            .offset(skip)
            .limit(limit)
        )
        categories = result.scalars().all()

        return [SupplementCategoryResponse.model_validate(category) for category in categories], total_count

    async def update_supplement_category(
        self, category_id: int, category_data: SupplementCategoryUpdate
    ) -> SupplementCategoryResponse:
        """Update a specific supplement category"""
        result = await self.db.execute(
            select(SupplementCategory).where(
                SupplementCategory.id == category_id, SupplementCategory.deleted_date.is_(None)
            )
        )
        category = result.scalars().first()
        if not category:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update fields if provided
        if category_data.name is not None:
            category.name = category_data.name
        if category_data.description is not None:
            category.description = category_data.description

        await self.db.commit()
        await self.db.refresh(category)

        return SupplementCategoryResponse.model_validate(category)

    async def delete_supplement_category(self, category_id: int) -> None:
        """Soft delete a specific supplement category"""
        result = await self.db.execute(
            select(SupplementCategory).where(
                SupplementCategory.id == category_id, SupplementCategory.deleted_date.is_(None)
            )
        )
        category = result.scalars().first()
        if not category:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        category.soft_delete()
        await self.db.commit()

    # ===== Supplement Methods =====
    async def create_supplement(self, user_id: int, supplement_data: SupplementCreate) -> SupplementResponse:
        """Create a new supplement"""
        new_supplement = Supplement(
            name=supplement_data.name,
            description=supplement_data.description,
            category_id=supplement_data.category_id,
            brand=supplement_data.brand,
            recommended_dosage=supplement_data.recommended_dosage,
            dosage_unit=supplement_data.dosage_unit,
            benefits=supplement_data.benefits,
            side_effects=supplement_data.side_effects,
            image_url=supplement_data.image_url,
            user_id=user_id,
            is_custom=supplement_data.is_custom,
        )
        self.db.add(new_supplement)
        await self.db.commit()
        await self.db.refresh(new_supplement)

        # Load the supplement with relationships for response
        result = await self.db.execute(
            select(Supplement).options(joinedload(Supplement.category)).where(Supplement.id == new_supplement.id)
        )
        supplement_with_relations = result.scalars().first()

        return SupplementResponse.model_validate(supplement_with_relations)

    async def get_supplement(self, supplement_id: int) -> SupplementResponse:
        """Get a specific supplement by ID with its category"""
        result = await self.db.execute(
            select(Supplement)
            .options(joinedload(Supplement.category))
            .where(Supplement.id == supplement_id, Supplement.deleted_date.is_(None))
        )
        supplement = result.scalars().first()
        if not supplement:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return SupplementResponse.model_validate(supplement)

    async def list_supplements(
        self, user_id: Optional[int] = None, category_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> Tuple[List[SupplementResponse], int]:
        """List supplements with optional filtering by user_id and category_id"""
        # Build base query
        base_query = select(Supplement).where(Supplement.deleted_date.is_(None))

        # Apply filters
        if user_id is not None:
            base_query = base_query.where((Supplement.user_id == user_id) | (Supplement.is_custom == 0))
        if category_id is not None:
            base_query = base_query.where(Supplement.category_id == category_id)

        # Get total count
        count_result = await self.db.execute(base_query)
        total_count = len(count_result.scalars().all())

        # Get paginated records with relationships
        result = await self.db.execute(
            base_query.options(joinedload(Supplement.category)).order_by(Supplement.name).offset(skip).limit(limit)
        )
        supplements = result.scalars().all()

        return [SupplementResponse.model_validate(supplement) for supplement in supplements], total_count

    async def update_supplement(
        self, supplement_id: int, user_id: int, supplement_data: SupplementUpdate
    ) -> SupplementResponse:
        """Update a specific supplement"""
        # Get the supplement with ownership check
        result = await self.db.execute(
            select(Supplement).where(
                Supplement.id == supplement_id, Supplement.user_id == user_id, Supplement.deleted_date.is_(None)
            )
        )
        supplement = result.scalars().first()
        if not supplement:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update fields if provided
        if supplement_data.name is not None:
            supplement.name = supplement_data.name
        if supplement_data.description is not None:
            supplement.description = supplement_data.description
        if supplement_data.category_id is not None:
            supplement.category_id = supplement_data.category_id
        if supplement_data.brand is not None:
            supplement.brand = supplement_data.brand
        if supplement_data.recommended_dosage is not None:
            supplement.recommended_dosage = supplement_data.recommended_dosage
        if supplement_data.dosage_unit is not None:
            supplement.dosage_unit = supplement_data.dosage_unit
        if supplement_data.benefits is not None:
            supplement.benefits = supplement_data.benefits
        if supplement_data.side_effects is not None:
            supplement.side_effects = supplement_data.side_effects
        if supplement_data.image_url is not None:
            supplement.image_url = supplement_data.image_url
        if supplement_data.is_custom is not None:
            supplement.is_custom = supplement_data.is_custom

        await self.db.commit()

        # Load the supplement with relationships for response
        result = await self.db.execute(
            select(Supplement).options(joinedload(Supplement.category)).where(Supplement.id == supplement_id)
        )
        updated_supplement = result.scalars().first()

        return SupplementResponse.model_validate(updated_supplement)

    async def delete_supplement(self, supplement_id: int, user_id: int) -> None:
        """Soft delete a specific supplement with ownership check"""
        result = await self.db.execute(
            select(Supplement).where(
                Supplement.id == supplement_id, Supplement.user_id == user_id, Supplement.deleted_date.is_(None)
            )
        )
        supplement = result.scalars().first()
        if not supplement:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        supplement.soft_delete()
        await self.db.commit()

    # ===== Diet Plan Methods =====
    async def create_diet_plan(self, user_id: int, plan_data: DietPlanCreate) -> DietPlanResponse:
        """Create a new diet plan with optional foods and supplements"""
        new_plan = DietPlan(
            user_id=user_id,
            name=plan_data.name,
            description=plan_data.description,
            goal=plan_data.goal,
            duration_days=plan_data.duration_days,
            daily_calories=plan_data.daily_calories,
            protein_target=plan_data.protein_target,
            carbs_target=plan_data.carbs_target,
            fat_target=plan_data.fat_target,
            is_public=plan_data.is_public,
        )
        self.db.add(new_plan)
        await self.db.flush()

        # Add foods to the plan if provided
        if plan_data.foods:
            for food_item in plan_data.foods:
                # Verify food exists and belongs to user or is public
                food = await self.db.get(Food, food_item.food_id)
                if not food or (food.user_id != user_id and food.is_custom == 1):
                    raise ExceptionBase(ErrorCode.NOT_FOUND, f"Food with ID {food_item.food_id} not found")

                # Insert into association table
                stmt = diet_plan_food.insert().values(
                    diet_plan_id=new_plan.id,
                    food_id=food_item.food_id,
                    meal_type=food_item.meal_type,
                    portion_size=food_item.portion_size,
                    portion_unit=food_item.portion_unit,
                    day_number=food_item.day_number,
                )
                await self.db.execute(stmt)

        # Add supplements to the plan if provided
        if plan_data.supplements:
            for supp_item in plan_data.supplements:
                # Verify supplement exists and belongs to user or is public
                supplement = await self.db.get(Supplement, supp_item.supplement_id)
                if not supplement or (supplement.user_id != user_id and supplement.is_custom == 1):
                    raise ExceptionBase(ErrorCode.NOT_FOUND, f"Supplement with ID {supp_item.supplement_id} not found")

                # Insert into association table
                stmt = diet_plan_supplement.insert().values(
                    diet_plan_id=new_plan.id,
                    supplement_id=supp_item.supplement_id,
                    dosage=supp_item.dosage,
                    dosage_unit=supp_item.dosage_unit,
                    time_of_day=supp_item.time_of_day,
                    day_number=supp_item.day_number,
                )
                await self.db.execute(stmt)

        await self.db.commit()
        await self.db.refresh(new_plan)

        # Load relationships for response
        query = (
            select(DietPlan)
            .where(DietPlan.id == new_plan.id)
            .options(
                joinedload(DietPlan.foods),
                joinedload(DietPlan.supplements),
            )
        )
        result = await self.db.execute(query)
        plan = result.unique().scalar_one_or_none()

        return DietPlanResponse.model_validate(plan)

    async def get_diet_plan(self, plan_id: int) -> DietPlanResponse:
        """Get a specific diet plan by ID with its foods and supplements"""
        query = (
            select(DietPlan)
            .where(DietPlan.id == plan_id)
            .options(
                joinedload(DietPlan.foods),
                joinedload(DietPlan.supplements),
            )
        )
        result = await self.db.execute(query)
        plan = result.unique().scalar_one_or_none()

        if not plan:
            raise ExceptionBase(ErrorCode.NOT_FOUND, f"Diet plan with ID {plan_id} not found")

        return DietPlanResponse.model_validate(plan)

    async def list_diet_plans(
        self, user_id: int, goal: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> Tuple[List[DietPlanResponse], int]:
        """List diet plans with optional filtering"""
        # Base query for counting total
        count_query = select(DietPlan).where(DietPlan.user_id == user_id)

        # Apply filters
        if goal:
            count_query = count_query.where(DietPlan.goal == goal)

        # Get total count
        count_result = await self.db.execute(select(func.count()).select_from(count_query.subquery()))
        total_count = count_result.scalar_one()

        # Query with pagination and eager loading
        query = (
            count_query.options(
                joinedload(DietPlan.foods),
                joinedload(DietPlan.supplements),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        plans = result.unique().scalars().all()

        return [DietPlanResponse.model_validate(plan) for plan in plans], total_count

    async def update_diet_plan(self, plan_id: int, user_id: int, plan_data: DietPlanUpdate) -> DietPlanResponse:
        """Update an existing diet plan"""
        # Get the plan and verify ownership
        plan = await self.db.get(DietPlan, plan_id)
        if not plan:
            raise ExceptionBase(ErrorCode.NOT_FOUND, f"Diet plan with ID {plan_id} not found")

        if plan.user_id != user_id:
            raise ExceptionBase(ErrorCode.FORBIDDEN, "You don't have permission to update this diet plan")

        # Update plan fields
        if plan_data.name is not None:
            plan.name = plan_data.name
        if plan_data.description is not None:
            plan.description = plan_data.description
        if plan_data.goal is not None:
            plan.goal = plan_data.goal
        if plan_data.duration_days is not None:
            plan.duration_days = plan_data.duration_days
        if plan_data.daily_calories is not None:
            plan.daily_calories = plan_data.daily_calories
        if plan_data.protein_target is not None:
            plan.protein_target = plan_data.protein_target
        if plan_data.carbs_target is not None:
            plan.carbs_target = plan_data.carbs_target
        if plan_data.fat_target is not None:
            plan.fat_target = plan_data.fat_target
        if plan_data.is_public is not None:
            plan.is_public = plan_data.is_public

        await self.db.commit()
        await self.db.refresh(plan)

        # Load relationships for response
        query = (
            select(DietPlan)
            .where(DietPlan.id == plan.id)
            .options(
                joinedload(DietPlan.foods),
                joinedload(DietPlan.supplements),
            )
        )
        result = await self.db.execute(query)
        updated_plan = result.unique().scalar_one_or_none()

        return DietPlanResponse.model_validate(updated_plan)

    async def delete_diet_plan(self, plan_id: int, user_id: int) -> None:
        """Delete a diet plan"""
        plan = await self.db.get(DietPlan, plan_id)
        if not plan:
            raise ExceptionBase(ErrorCode.NOT_FOUND, f"Diet plan with ID {plan_id} not found")

        if plan.user_id != user_id:
            raise ExceptionBase(ErrorCode.FORBIDDEN, "You don't have permission to delete this diet plan")

        await self.db.delete(plan)
        await self.db.commit()

    # ===== Meal Template Methods =====
    async def create_meal_template(self, user_id: int, template_data: MealTemplateCreate) -> MealTemplateResponse:
        """Create a new meal template with foods"""
        new_template = MealTemplate(
            user_id=user_id,
            name=template_data.name,
            description=template_data.description,
            meal_type=template_data.meal_type,
            is_favorite=template_data.is_favorite,
        )
        self.db.add(new_template)
        await self.db.flush()

        # Add foods to the template
        for food_item in template_data.foods:
            # Verify food exists and belongs to user or is public
            food = await self.db.get(Food, food_item.food_id)
            if not food or (food.user_id != user_id and food.is_custom == 1):
                raise ExceptionBase(ErrorCode.NOT_FOUND, f"Food with ID {food_item.food_id} not found")

            template_food = MealTemplateFood(
                template_id=new_template.id,
                food_id=food_item.food_id,
                portion_size=food_item.portion_size,
                portion_unit=food_item.portion_unit,
            )
            self.db.add(template_food)

        await self.db.commit()
        await self.db.refresh(new_template)

        # Load relationships for response
        query = (
            select(MealTemplate)
            .where(MealTemplate.id == new_template.id)
            .options(joinedload(MealTemplate.meal_foods).joinedload(MealTemplateFood.food))
        )
        result = await self.db.execute(query)
        template = result.unique().scalar_one_or_none()

        return MealTemplateResponse.model_validate(template)

    async def get_meal_template(self, template_id: int) -> MealTemplateResponse:
        """Get a specific meal template by ID with its foods"""
        query = (
            select(MealTemplate)
            .where(MealTemplate.id == template_id)
            .options(joinedload(MealTemplate.meal_foods).joinedload(MealTemplateFood.food))
        )
        result = await self.db.execute(query)
        template = result.unique().scalar_one_or_none()

        if not template:
            raise ExceptionBase(ErrorCode.NOT_FOUND, f"Meal template with ID {template_id} not found")

        return MealTemplateResponse.model_validate(template)

    async def list_meal_templates(
        self, user_id: int, meal_type: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> Tuple[List[MealTemplateResponse], int]:
        """List meal templates with optional filtering"""
        # Base query for counting total
        count_query = select(MealTemplate).where(MealTemplate.user_id == user_id)

        # Apply filters
        if meal_type:
            count_query = count_query.where(MealTemplate.meal_type == meal_type)

        # Get total count
        count_result = await self.db.execute(select(func.count()).select_from(count_query.subquery()))
        total_count = count_result.scalar_one()

        # Query with pagination and eager loading
        query = (
            count_query.options(joinedload(MealTemplate.meal_foods).joinedload(MealTemplateFood.food))
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        templates = result.unique().scalars().all()

        return [MealTemplateResponse.model_validate(template) for template in templates], total_count

    async def update_meal_template(
        self, template_id: int, user_id: int, template_data: MealTemplateUpdate
    ) -> MealTemplateResponse:
        """Update an existing meal template"""
        # Get the template and verify ownership
        template = await self.db.get(MealTemplate, template_id)
        if not template:
            raise ExceptionBase(ErrorCode.NOT_FOUND, f"Meal template with ID {template_id} not found")

        if template.user_id != user_id:
            raise ExceptionBase(ErrorCode.FORBIDDEN, "You don't have permission to update this meal template")

        # Update template fields
        if template_data.name is not None:
            template.name = template_data.name
        if template_data.description is not None:
            template.description = template_data.description
        if template_data.meal_type is not None:
            template.meal_type = template_data.meal_type
        if template_data.is_favorite is not None:
            template.is_favorite = template_data.is_favorite

        # Update foods if provided
        if template_data.foods is not None:
            # Delete existing template foods
            query = select(MealTemplateFood).where(MealTemplateFood.template_id == template_id)
            result = await self.db.execute(query)
            existing_foods = result.scalars().all()
            for food in existing_foods:
                await self.db.delete(food)

            # Add new foods
            for food_item in template_data.foods:
                # Verify food exists and belongs to user or is public
                food = await self.db.get(Food, food_item.food_id)
                if not food or (food.user_id != user_id and food.is_custom == 1):
                    raise ExceptionBase(ErrorCode.NOT_FOUND, f"Food with ID {food_item.food_id} not found")

                template_food = MealTemplateFood(
                    template_id=template.id,
                    food_id=food_item.food_id,
                    portion_size=food_item.portion_size,
                    portion_unit=food_item.portion_unit,
                )
                self.db.add(template_food)

        await self.db.commit()
        await self.db.refresh(template)

        # Load relationships for response
        query = (
            select(MealTemplate)
            .where(MealTemplate.id == template.id)
            .options(joinedload(MealTemplate.meal_foods).joinedload(MealTemplateFood.food))
        )
        result = await self.db.execute(query)
        updated_template = result.unique().scalar_one_or_none()

        return MealTemplateResponse.model_validate(updated_template)

    async def delete_meal_template(self, template_id: int, user_id: int) -> None:
        """Delete a meal template"""
        template = await self.db.get(MealTemplate, template_id)
        if not template:
            raise ExceptionBase(ErrorCode.NOT_FOUND, f"Meal template with ID {template_id} not found")

        if template.user_id != user_id:
            raise ExceptionBase(ErrorCode.FORBIDDEN, "You don't have permission to delete this meal template")

        await self.db.delete(template)
        await self.db.commit()
