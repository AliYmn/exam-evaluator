from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FoodBase(BaseModel):
    """Base model for Food data"""

    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class FoodCreate(FoodBase):
    """Request model for creating a Food record"""


class FoodUpdate(FoodBase):
    """Request model for updating a Food record"""

    name: Optional[str] = None


class FoodResponse(FoodBase):
    """Response model for Food data"""

    id: int

    class Config:
        from_attributes = True


class FoodListResponse(BaseModel):
    """Response model for a list of Food records"""

    items: List[FoodResponse]
    count: int
    total: int
