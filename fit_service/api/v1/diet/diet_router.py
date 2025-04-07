from fastapi import APIRouter, Depends, Query, status, Header, Path
from typing import Annotated, Optional

from fit_service.api.v1.diet.diet_schemas import (
    FoodCategoryCreate,
    FoodCategoryUpdate,
    FoodCategoryResponse,
    FoodCategoryListResponse,
    FoodCreate,
    FoodUpdate,
    FoodResponse,
    FoodListResponse,
    SupplementCategoryCreate,
    SupplementCategoryUpdate,
    SupplementCategoryResponse,
    SupplementCategoryListResponse,
    SupplementCreate,
    SupplementUpdate,
    SupplementResponse,
    SupplementListResponse,
    DietPlanCreate,
    DietPlanUpdate,
    DietPlanResponse,
    DietPlanListResponse,
    MealTemplateCreate,
    MealTemplateUpdate,
    MealTemplateResponse,
    MealTemplateListResponse,
)
from fit_service.core.services.diet_service import DietService
from sqlalchemy.ext.asyncio import AsyncSession
from libs.db import get_async_db
from libs.service.auth import AuthService
from libs import ErrorCode, ExceptionBase

router = APIRouter(tags=["Diet"], prefix="/diet")


def get_diet_service(db: AsyncSession = Depends(get_async_db)) -> DietService:
    return DietService(db)


def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


# ===== Food Category Routes =====
@router.post("/food-categories", response_model=FoodCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_food_category(
    category_data: FoodCategoryCreate,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Create a new food category (admin only)"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        if user.role != "admin":
            raise ExceptionBase(ErrorCode.FORBIDDEN)
        return await diet_service.create_food_category(category_data)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.get("/food-categories/{category_id}", response_model=FoodCategoryResponse)
async def get_food_category(
    category_id: int = Path(..., description="The ID of the food category"),
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get a specific food category by ID"""
    await auth_service.get_user_from_token(authorization)
    return await diet_service.get_food_category(category_id)


@router.get("/food-categories", response_model=FoodCategoryListResponse)
async def list_food_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """List all food categories with pagination"""
    await auth_service.get_user_from_token(authorization)
    categories, total_count = await diet_service.list_food_categories(skip, limit)
    return FoodCategoryListResponse(
        items=categories,
        total=total_count,
    )


@router.put("/food-categories/{category_id}", response_model=FoodCategoryResponse)
async def update_food_category(
    category_id: int,
    category_data: FoodCategoryUpdate,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update a specific food category (admin only)"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        if user.role != "admin":
            raise ExceptionBase(ErrorCode.FORBIDDEN)
        return await diet_service.update_food_category(category_id, category_data)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.delete("/food-categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_food_category(
    category_id: int,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Delete a specific food category (admin only)"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        if user.role != "admin":
            raise ExceptionBase(ErrorCode.FORBIDDEN)
        await diet_service.delete_food_category(category_id)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


# ===== Food Routes =====
@router.post("/foods", response_model=FoodResponse, status_code=status.HTTP_201_CREATED)
async def create_food(
    food_data: FoodCreate,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Create a new food"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await diet_service.create_food(user.id, food_data)
    except Exception:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.get("/foods/{food_id}", response_model=FoodResponse)
async def get_food(
    food_id: int = Path(..., description="The ID of the food"),
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get a specific food by ID with its category"""
    await auth_service.get_user_from_token(authorization)
    return await diet_service.get_food(food_id)


@router.get("/foods", response_model=FoodListResponse)
async def list_foods(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """List foods with optional filtering"""
    user = await auth_service.get_user_from_token(authorization)
    foods, total_count = await diet_service.list_foods(user_id=user.id, category_id=category_id, skip=skip, limit=limit)
    return FoodListResponse(
        items=foods,
        total=total_count,
    )


@router.put("/foods/{food_id}", response_model=FoodResponse)
async def update_food(
    food_id: int,
    food_data: FoodUpdate,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update a specific food"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await diet_service.update_food(food_id, user.id, food_data)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.delete("/foods/{food_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_food(
    food_id: int,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Delete a specific food"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        await diet_service.delete_food(food_id, user.id)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


# ===== Supplement Category Routes =====
@router.post("/supplement-categories", response_model=SupplementCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_supplement_category(
    category_data: SupplementCategoryCreate,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Create a new supplement category (admin only)"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        if user.role != "admin":
            raise ExceptionBase(ErrorCode.FORBIDDEN)
        return await diet_service.create_supplement_category(category_data)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.get("/supplement-categories/{category_id}", response_model=SupplementCategoryResponse)
async def get_supplement_category(
    category_id: int = Path(..., description="The ID of the supplement category"),
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get a specific supplement category by ID"""
    await auth_service.get_user_from_token(authorization)
    return await diet_service.get_supplement_category(category_id)


@router.get("/supplement-categories", response_model=SupplementCategoryListResponse)
async def list_supplement_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """List all supplement categories with pagination"""
    await auth_service.get_user_from_token(authorization)
    categories, total_count = await diet_service.list_supplement_categories(skip, limit)
    return SupplementCategoryListResponse(
        items=categories,
        total=total_count,
    )


@router.put("/supplement-categories/{category_id}", response_model=SupplementCategoryResponse)
async def update_supplement_category(
    category_id: int,
    category_data: SupplementCategoryUpdate,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update a specific supplement category (admin only)"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        if user.role != "admin":
            raise ExceptionBase(ErrorCode.FORBIDDEN)
        return await diet_service.update_supplement_category(category_id, category_data)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.delete("/supplement-categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplement_category(
    category_id: int,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Delete a specific supplement category (admin only)"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        if user.role != "admin":
            raise ExceptionBase(ErrorCode.FORBIDDEN)
        await diet_service.delete_supplement_category(category_id)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


# ===== Supplement Routes =====
@router.post("/supplements", response_model=SupplementResponse, status_code=status.HTTP_201_CREATED)
async def create_supplement(
    supplement_data: SupplementCreate,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Create a new supplement"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await diet_service.create_supplement(user.id, supplement_data)
    except Exception:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.get("/supplements/{supplement_id}", response_model=SupplementResponse)
async def get_supplement(
    supplement_id: int = Path(..., description="The ID of the supplement"),
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get a specific supplement by ID with its category"""
    await auth_service.get_user_from_token(authorization)
    return await diet_service.get_supplement(supplement_id)


@router.get("/supplements", response_model=SupplementListResponse)
async def list_supplements(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """List supplements with optional filtering"""
    user = await auth_service.get_user_from_token(authorization)
    supplements, total_count = await diet_service.list_supplements(
        user_id=user.id, category_id=category_id, skip=skip, limit=limit
    )
    return SupplementListResponse(
        items=supplements,
        total=total_count,
    )


@router.put("/supplements/{supplement_id}", response_model=SupplementResponse)
async def update_supplement(
    supplement_id: int,
    supplement_data: SupplementUpdate,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update a specific supplement"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await diet_service.update_supplement(supplement_id, user.id, supplement_data)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.delete("/supplements/{supplement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplement(
    supplement_id: int,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Delete a specific supplement"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        await diet_service.delete_supplement(supplement_id, user.id)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


# ===== Diet Plan Routes =====
@router.post("/plans", response_model=DietPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_diet_plan(
    plan_data: DietPlanCreate,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Create a new diet plan with optional foods and supplements"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await diet_service.create_diet_plan(user.id, plan_data)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.get("/plans/{plan_id}", response_model=DietPlanResponse)
async def get_diet_plan(
    plan_id: int = Path(..., description="The ID of the diet plan"),
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get a specific diet plan by ID with its foods and supplements"""
    await auth_service.get_user_from_token(authorization)
    return await diet_service.get_diet_plan(plan_id)


@router.get("/plans", response_model=DietPlanListResponse)
async def list_diet_plans(
    goal: Optional[str] = Query(None, description="Filter by goal"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """List diet plans with optional filtering"""
    user = await auth_service.get_user_from_token(authorization)
    plans, total_count = await diet_service.list_diet_plans(user_id=user.id, goal=goal, skip=skip, limit=limit)
    return DietPlanListResponse(
        items=plans,
        total=total_count,
    )


@router.put("/plans/{plan_id}", response_model=DietPlanResponse)
async def update_diet_plan(
    plan_id: int,
    plan_data: DietPlanUpdate,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update a specific diet plan"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await diet_service.update_diet_plan(plan_id, user.id, plan_data)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diet_plan(
    plan_id: int,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Delete a specific diet plan"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        await diet_service.delete_diet_plan(plan_id, user.id)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


# ===== Meal Template Routes =====
@router.post("/meal-templates", response_model=MealTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_meal_template(
    template_data: MealTemplateCreate,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Create a new meal template with foods"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await diet_service.create_meal_template(user.id, template_data)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.get("/meal-templates/{template_id}", response_model=MealTemplateResponse)
async def get_meal_template(
    template_id: int = Path(..., description="The ID of the meal template"),
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get a specific meal template by ID with its foods"""
    await auth_service.get_user_from_token(authorization)
    return await diet_service.get_meal_template(template_id)


@router.get("/meal-templates", response_model=MealTemplateListResponse)
async def list_meal_templates(
    meal_type: Optional[str] = Query(None, description="Filter by meal type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """List meal templates with optional filtering"""
    user = await auth_service.get_user_from_token(authorization)
    templates, total_count = await diet_service.list_meal_templates(
        user_id=user.id, meal_type=meal_type, skip=skip, limit=limit
    )
    return MealTemplateListResponse(
        items=templates,
        total=total_count,
    )


@router.put("/meal-templates/{template_id}", response_model=MealTemplateResponse)
async def update_meal_template(
    template_id: int,
    template_data: MealTemplateUpdate,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update a specific meal template"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        return await diet_service.update_meal_template(template_id, user.id, template_data)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.delete("/meal-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal_template(
    template_id: int,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Delete a specific meal template"""
    try:
        user = await auth_service.get_user_from_token(authorization)
        await diet_service.delete_meal_template(template_id, user.id)
    except Exception as e:
        if isinstance(e, ExceptionBase):
            raise e
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)
