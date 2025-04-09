from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, time


# Fasting Plan schemas
class FastingPlanBase(BaseModel):
    """Base model for Fasting Plan data"""

    fasting_type: str = Field(..., description="Fasting type (e.g., '16:8', '18:6', '20:4', 'OMAD')")
    is_active: bool = Field(True, description="Whether this plan is currently active")
    target_calories: Optional[int] = Field(None, description="Daily calorie target during eating window")
    target_meals: Optional[int] = Field(None, description="Target number of meals during eating window")
    target_water: Optional[float] = Field(None, description="Target water intake in liters")
    target_protein: Optional[float] = Field(None, description="Target protein intake in grams")
    target_carb: Optional[float] = Field(None, description="Target carbohydrate intake in grams")
    target_fat: Optional[float] = Field(None, description="Target fat intake in grams")


class FastingPlanCreate(FastingPlanBase):
    """Request model for creating a Fasting Plan"""


class FastingPlanUpdate(BaseModel):
    """Request model for updating a Fasting Plan"""

    fasting_type: Optional[str] = Field(None, description="Fasting type (e.g., '16:8', '18:6', '20:4', 'OMAD')")
    is_active: Optional[bool] = Field(None, description="Whether this plan is currently active")
    target_calories: Optional[int] = Field(None, description="Daily calorie target during eating window")
    target_meals: Optional[int] = Field(None, description="Target number of meals during eating window")
    target_water: Optional[float] = Field(None, description="Target water intake in liters")
    target_protein: Optional[float] = Field(None, description="Target protein intake in grams")
    target_carb: Optional[float] = Field(None, description="Target carbohydrate intake in grams")
    target_fat: Optional[float] = Field(None, description="Target fat intake in grams")


class FastingPlanResponse(FastingPlanBase):
    """Response model for Fasting Plan data"""

    id: int
    user_id: int
    created_date: datetime

    class Config:
        from_attributes = True


class FastingPlanListResponse(BaseModel):
    """Response model for a list of Fasting Plan records"""

    items: List[FastingPlanResponse]
    count: int
    total: int


# Fasting Session schemas
class FastingSessionBase(BaseModel):
    """Base model for Fasting Session data"""

    start_time: time = Field(..., description="When this fasting session started")
    end_time: Optional[time] = Field(None, description="When this fasting session ended (null if ongoing)")
    mood: Optional[str] = Field(None, description="User's mood during fasting (can store emoji)")
    stage: Optional[str] = Field(None, description="Fasting stage (e.g., 'anabolic', 'catabolic', 'ketosis')")


class FastingSessionCreate(FastingSessionBase):
    """Request model for creating a Fasting Session"""

    plan_id: Optional[int] = Field(None, description="ID of the associated fasting plan")


class FastingSessionUpdate(BaseModel):
    """Request model for updating a Fasting Session"""

    end_time: Optional[time] = Field(None, description="When this fasting session ended")
    status: Optional[Literal["PENDING", "STARTED", "FAILED", "COMPLETED"]] = Field(
        None, description="Status of the fasting session"
    )
    mood: Optional[str] = Field(None, description="User's mood during fasting (can store emoji)")
    stage: Optional[str] = Field(None, description="Fasting stage (e.g., 'anabolic', 'catabolic', 'ketosis')")


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
    calories: Optional[int] = Field(None, description="Estimated calories")
    protein: Optional[float] = Field(None, description="Protein in grams")
    carbs: Optional[float] = Field(None, description="Carbohydrates in grams")
    fat: Optional[float] = Field(None, description="Fat in grams")
    detailed_macros: Optional[Dict[str, Any]] = Field(None, description="Detailed breakdown of nutrients")


class FastingMealLogCreate(FastingMealLogBase):
    """Request model for creating a Fasting Meal Log"""


class FastingMealLogUpdate(BaseModel):
    """Request model for updating a Fasting Meal Log"""

    photo_url: Optional[str] = Field(None, description="URL to the uploaded photo")
    notes: Optional[str] = Field(None, description="User notes about the meal")
    calories: Optional[int] = Field(None, description="Estimated calories")
    protein: Optional[float] = Field(None, description="Protein in grams")
    carbs: Optional[float] = Field(None, description="Carbohydrates in grams")
    fat: Optional[float] = Field(None, description="Fat in grams")
    detailed_macros: Optional[Dict[str, Any]] = Field(None, description="Detailed breakdown of nutrients")


class FastingMealLogResponse(FastingMealLogBase):
    """Response model for Fasting Meal Log"""

    id: int
    user_id: int
    created_date: datetime

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
