from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# Fasting Plan schemas
class FastingPlanBase(BaseModel):
    """Base model for Fasting Plan data"""

    fasting_hours: int = Field(..., description="Number of hours to fast")
    eating_hours: int = Field(..., description="Number of hours to eat")
    target_week: Optional[int] = Field(None, description="Target number of weeks for this fasting plan")
    current_week: Optional[int] = Field(0, description="Current week of this fasting plan")
    start_date: Optional[datetime] = Field(None, description="Target start date and time for this fasting plan")
    finish_date: Optional[datetime] = Field(None, description="Target finish date and time for this fasting plan")
    target_meals: Optional[int] = Field(None, description="Target number of meals per day")
    mood: Optional[str] = Field(None, description="User mood")
    stage: Optional[str] = Field(None, description="User stage")
    status: Optional[str] = Field(None, description="Status of the fasting plan")
    rate: Optional[float] = Field(0, description="Rate of calories burned")


class FastingPlanCreate(FastingPlanBase):
    """Request model for creating a Fasting Plan"""


class FastingPlanResponse(BaseModel):
    """Response model for Fasting Plan data"""

    id: int
    user_id: int
    fasting_hours: Optional[int] = None
    eating_hours: Optional[int] = None
    target_week: Optional[int] = None
    current_week: Optional[int] = None
    start_date: Optional[datetime] = None
    finish_date: Optional[datetime] = None
    created_date: datetime
    status: Optional[str] = None
    mood: Optional[str] = None
    stage: Optional[str] = None
    target_calories: Optional[int] = None
    target_meals: Optional[int] = None
    target_water: Optional[float] = None
    target_protein: Optional[float] = None
    target_carb: Optional[float] = None
    target_fat: Optional[float] = None
    rate: Optional[float] = 0

    class Config:
        from_attributes = True


class FastingPlanListResponse(BaseModel):
    """Response model for a list of Fasting Plan records"""

    items: List[FastingPlanResponse]
    count: int
    total: int


# Fasting Meal Log schemas
class FastingMealLogBase(BaseModel):
    """Base model for Fasting Meal Log"""

    plan_id: int = Field(..., description="ID of the associated fasting plan")
    title: Optional[str] = Field(None, description="Title of the meal")
    photo_url: Optional[str] = Field(None, description="URL to the uploaded photo")
    notes: Optional[str] = Field(None, description="User notes about the meal")
    calories: Optional[int] = Field(None, description="Estimated calories")
    protein: Optional[float] = Field(None, description="Protein in grams")
    carbs: Optional[float] = Field(None, description="Carbohydrates in grams")
    fat: Optional[float] = Field(None, description="Fat in grams")
    detailed_macros: Optional[Dict[str, Any]] = Field(None, description="Detailed breakdown of nutrients")
    ai_content: Optional[str] = Field(None, description="AI generated content")
    rate: Optional[float] = Field(0, description="Rate of calories burned")


class FastingMealLogCreate(FastingMealLogBase):
    """Request model for creating a Fasting Meal Log"""


class FastingMealLogUpdate(BaseModel):
    """Request model for updating a Fasting Meal Log"""

    title: Optional[str] = Field(None, description="Title of the meal")
    photo_url: Optional[str] = Field(None, description="URL to the uploaded photo")
    notes: Optional[str] = Field(None, description="User notes about the meal")


class FastingMealLogResponse(FastingMealLogBase):
    """Response model for Fasting Meal Log"""

    id: int
    user_id: int
    created_date: datetime
    ai_content: Optional[str] = None
    rate: Optional[float] = 0

    class Config:
        from_attributes = True


class FastingMealLogListResponse(BaseModel):
    """Response model for a list of Fasting Meal Logs"""

    items: List[FastingMealLogResponse]
    count: int
    total: int


# Fasting Workout Log schemas
class FastingWorkoutLogBase(BaseModel):
    """Base model for Fasting Workout Log"""

    plan_id: int = Field(..., description="ID of the associated fasting plan")
    workout_name: str = Field(..., description="Name of the workout")
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes")
    calories_burned: Optional[int] = Field(None, description="Estimated calories burned")
    intensity: Optional[str] = Field(None, description="Workout intensity (Low, Medium, High)")
    notes: Optional[str] = Field(None, description="User notes about the workout")
    ai_content: Optional[str] = Field(None, description="AI generated content")
    rate: Optional[float] = Field(0, description="Rate of calories burned")


class FastingWorkoutLogCreate(FastingWorkoutLogBase):
    """Request model for creating a Fasting Workout Log"""


class FastingWorkoutLogUpdate(BaseModel):
    """Request model for updating a Fasting Workout Log"""

    workout_name: Optional[str] = Field(None, description="Name of the workout")
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes")
    calories_burned: Optional[int] = Field(None, description="Estimated calories burned")
    intensity: Optional[str] = Field(None, description="Workout intensity (Low, Medium, High)")
    notes: Optional[str] = Field(None, description="User notes about the workout")
    rate: Optional[float] = Field(0, description="Rate of calories burned")


class FastingWorkoutLogResponse(FastingWorkoutLogBase):
    """Response model for Fasting Workout Log"""

    id: int
    user_id: int
    created_date: datetime

    class Config:
        from_attributes = True


class FastingWorkoutLogListResponse(BaseModel):
    """Response model for a list of Fasting Workout Logs"""

    items: List[FastingWorkoutLogResponse]
    count: int
    total: int
