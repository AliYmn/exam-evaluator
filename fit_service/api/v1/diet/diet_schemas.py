from typing import List, Optional
from pydantic import BaseModel


# FoodCategory schemas
class FoodCategoryBase(BaseModel):
    """Base model for FoodCategory data"""

    name: str
    description: Optional[str] = None


class FoodCategoryCreate(FoodCategoryBase):
    """Request model for creating a FoodCategory"""


class FoodCategoryUpdate(BaseModel):
    """Request model for updating a FoodCategory"""

    name: Optional[str] = None
    description: Optional[str] = None


class FoodCategoryResponse(FoodCategoryBase):
    """Response model for FoodCategory data"""

    id: int

    class Config:
        from_attributes = True


class FoodCategoryListResponse(BaseModel):
    """Response model for a list of FoodCategory records"""

    items: List[FoodCategoryResponse]
    total: int


# Food schemas
class FoodBase(BaseModel):
    """Base model for Food data"""

    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    serving_size: Optional[float] = None
    serving_unit: Optional[str] = None
    image_url: Optional[str] = None
    is_custom: Optional[int] = 1  # Default to custom food


class FoodCreate(FoodBase):
    """Request model for creating a Food"""


class FoodUpdate(BaseModel):
    """Request model for updating a Food"""

    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    serving_size: Optional[float] = None
    serving_unit: Optional[str] = None
    image_url: Optional[str] = None
    is_custom: Optional[int] = None


class FoodResponse(FoodBase):
    """Response model for Food data"""

    id: int
    user_id: Optional[int] = None
    category: Optional[FoodCategoryResponse] = None

    class Config:
        from_attributes = True


class FoodListResponse(BaseModel):
    """Response model for a list of Food records"""

    items: List[FoodResponse]
    total: int


# SupplementCategory schemas
class SupplementCategoryBase(BaseModel):
    """Base model for SupplementCategory data"""

    name: str
    description: Optional[str] = None


class SupplementCategoryCreate(SupplementCategoryBase):
    """Request model for creating a SupplementCategory"""


class SupplementCategoryUpdate(BaseModel):
    """Request model for updating a SupplementCategory"""

    name: Optional[str] = None
    description: Optional[str] = None


class SupplementCategoryResponse(SupplementCategoryBase):
    """Response model for SupplementCategory data"""

    id: int

    class Config:
        from_attributes = True


class SupplementCategoryListResponse(BaseModel):
    """Response model for a list of SupplementCategory records"""

    items: List[SupplementCategoryResponse]
    total: int


# Supplement schemas
class SupplementBase(BaseModel):
    """Base model for Supplement data"""

    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    recommended_dosage: Optional[float] = None
    dosage_unit: Optional[str] = None
    benefits: Optional[str] = None
    side_effects: Optional[str] = None
    image_url: Optional[str] = None
    is_custom: Optional[int] = 1  # Default to custom supplement


class SupplementCreate(SupplementBase):
    """Request model for creating a Supplement"""


class SupplementUpdate(BaseModel):
    """Request model for updating a Supplement"""

    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    recommended_dosage: Optional[float] = None
    dosage_unit: Optional[str] = None
    benefits: Optional[str] = None
    side_effects: Optional[str] = None
    image_url: Optional[str] = None
    is_custom: Optional[int] = None


class SupplementResponse(SupplementBase):
    """Response model for Supplement data"""

    id: int
    user_id: Optional[int] = None
    category: Optional[SupplementCategoryResponse] = None

    class Config:
        from_attributes = True


class SupplementListResponse(BaseModel):
    """Response model for a list of Supplement records"""

    items: List[SupplementResponse]
    total: int


# DietPlan schemas
class DietPlanFoodItem(BaseModel):
    """Model for a food item in a diet plan"""

    food_id: int
    meal_type: str  # breakfast, lunch, dinner, snack
    portion_size: float
    portion_unit: str
    day_number: int = 1


class DietPlanSupplementItem(BaseModel):
    """Model for a supplement item in a diet plan"""

    supplement_id: int
    dosage: float
    dosage_unit: str
    time_of_day: str  # morning, afternoon, evening, pre-workout, post-workout
    day_number: int = 1


class DietPlanBase(BaseModel):
    """Base model for DietPlan data"""

    name: str
    description: Optional[str] = None
    goal: Optional[str] = None
    duration_days: Optional[int] = None
    daily_calories: Optional[float] = None
    protein_target: Optional[float] = None
    carbs_target: Optional[float] = None
    fat_target: Optional[float] = None
    is_public: Optional[int] = 0


class DietPlanCreate(DietPlanBase):
    """Request model for creating a DietPlan"""

    foods: Optional[List[DietPlanFoodItem]] = None
    supplements: Optional[List[DietPlanSupplementItem]] = None


class DietPlanUpdate(BaseModel):
    """Request model for updating a DietPlan"""

    name: Optional[str] = None
    description: Optional[str] = None
    goal: Optional[str] = None
    duration_days: Optional[int] = None
    daily_calories: Optional[float] = None
    protein_target: Optional[float] = None
    carbs_target: Optional[float] = None
    fat_target: Optional[float] = None
    is_public: Optional[int] = None


class DietPlanFoodResponse(BaseModel):
    """Response model for a food item in a diet plan"""

    food: FoodResponse
    meal_type: str
    portion_size: float
    portion_unit: str
    day_number: int

    class Config:
        from_attributes = True


class DietPlanSupplementResponse(BaseModel):
    """Response model for a supplement item in a diet plan"""

    supplement: SupplementResponse
    dosage: float
    dosage_unit: str
    time_of_day: str
    day_number: int

    class Config:
        from_attributes = True


class DietPlanResponse(DietPlanBase):
    """Response model for DietPlan data"""

    id: int
    user_id: int
    foods: List[DietPlanFoodResponse] = []
    supplements: List[DietPlanSupplementResponse] = []

    class Config:
        from_attributes = True


class DietPlanListResponse(BaseModel):
    """Response model for a list of DietPlan records"""

    items: List[DietPlanResponse]
    total: int


# MealTemplate schemas
class MealTemplateFoodItem(BaseModel):
    """Model for a food item in a meal template"""

    food_id: int
    portion_size: float
    portion_unit: str


class MealTemplateBase(BaseModel):
    """Base model for MealTemplate data"""

    name: str
    description: Optional[str] = None
    meal_type: str  # breakfast, lunch, dinner, snack
    is_favorite: Optional[bool] = False


class MealTemplateCreate(MealTemplateBase):
    """Request model for creating a MealTemplate"""

    foods: List[MealTemplateFoodItem]


class MealTemplateUpdate(BaseModel):
    """Request model for updating a MealTemplate"""

    name: Optional[str] = None
    description: Optional[str] = None
    meal_type: Optional[str] = None
    is_favorite: Optional[bool] = None
    foods: Optional[List[MealTemplateFoodItem]] = None


class MealTemplateFoodResponse(BaseModel):
    """Response model for a food item in a meal template"""

    id: int
    food: FoodResponse
    portion_size: float
    portion_unit: str

    class Config:
        from_attributes = True


class MealTemplateResponse(MealTemplateBase):
    """Response model for MealTemplate data"""

    id: int
    user_id: int
    meal_foods: List[MealTemplateFoodResponse] = []

    class Config:
        from_attributes = True


class MealTemplateListResponse(BaseModel):
    """Response model for a list of MealTemplate records"""

    items: List[MealTemplateResponse]
    total: int
