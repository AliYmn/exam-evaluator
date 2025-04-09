from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, time


# Fasting Plan schemas
class FastingPlanBase(BaseModel):
    """Base model for Fasting Plan data"""

    fasting_hours: int = Field(..., description="Number of hours to fast")
    eating_hours: int = Field(..., description="Number of hours to eat")
    target_week: Optional[int] = Field(None, description="Target number of weeks for this fasting plan")
    current_week: Optional[int] = Field(0, description="Current week of this fasting plan")
    start_date: Optional[datetime] = Field(None, description="Target start date and time for this fasting plan")
    finish_date: Optional[datetime] = Field(None, description="Target finish date and time for this fasting plan")


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

    class Config:
        from_attributes = True


class FastingSessionResponse(BaseModel):
    """Response model for Fasting Session data"""

    id: int
    user_id: int
    plan_id: Optional[int] = None
    start_time: time
    end_time: Optional[time] = None
    status: str
    mood: Optional[str] = None
    stage: Optional[str] = None
    target_calories: Optional[int] = None
    target_meals: Optional[int] = None
    target_water: Optional[float] = None
    target_protein: Optional[float] = None
    target_carb: Optional[float] = None
    target_fat: Optional[float] = None
    fasting_hours: Optional[int] = None
    eating_hours: Optional[int] = None
    target_week: Optional[int] = None
    current_week: Optional[int] = None
    created_date: datetime

    class Config:
        from_attributes = True


class FastingSessionListResponse(BaseModel):
    """Response model for a list of Fasting Session records"""

    items: List[FastingSessionResponse]
    count: int
    total: int


# Fasting Meal Log schemas
class FastingMealLogBase(BaseModel):
    """Base model for Fasting Meal Log"""

    session_id: int = Field(..., description="ID of the associated fasting session")
    photo_url: Optional[str] = Field(None, description="URL to the uploaded photo")
    notes: Optional[str] = Field(None, description="User notes about the meal")


class FastingMealLogCreate(FastingMealLogBase):
    """Request model for creating a Fasting Meal Log"""


class FastingMealLogUpdate(BaseModel):
    """Request model for updating a Fasting Meal Log"""

    photo_url: Optional[str] = Field(None, description="URL to the uploaded photo")
    notes: Optional[str] = Field(None, description="User notes about the meal")


class FastingMealLogResponse(FastingMealLogBase):
    """Response model for Fasting Meal Log"""

    id: int
    user_id: int
    created_date: datetime
    ai_content: Optional[str] = None

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

    session_id: int = Field(..., description="ID of the associated fasting session")
    workout_name: str = Field(..., description="Name of the workout")
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes")
    calories_burned: Optional[int] = Field(None, description="Estimated calories burned")
    intensity: Optional[str] = Field(None, description="Workout intensity (Low, Medium, High)")
    notes: Optional[str] = Field(None, description="User notes about the workout")
    ai_content: Optional[str] = Field(None, description="AI generated content")


class FastingWorkoutLogCreate(FastingWorkoutLogBase):
    """Request model for creating a Fasting Workout Log"""


class FastingWorkoutLogUpdate(BaseModel):
    """Request model for updating a Fasting Workout Log"""

    workout_name: Optional[str] = Field(None, description="Name of the workout")
    duration_minutes: Optional[int] = Field(None, description="Duration in minutes")
    calories_burned: Optional[int] = Field(None, description="Estimated calories burned")
    intensity: Optional[str] = Field(None, description="Workout intensity (Low, Medium, High)")
    notes: Optional[str] = Field(None, description="User notes about the workout")


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
