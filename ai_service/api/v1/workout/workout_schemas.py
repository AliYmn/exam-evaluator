from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkoutBase(BaseModel):
    """Base model for Workout data"""

    name: str
    description: Optional[str] = None
    workout_type: Optional[str] = None
    target_muscles: List[str] = Field(default_factory=list)
    duration_minutes: Optional[float] = None
    calories_burned: Optional[float] = None
    equipment: Optional[str] = None
    difficulty: Optional[str] = None
    instructions: Dict[str, Any] = Field(default_factory=dict)


class WorkoutCreate(WorkoutBase):
    """Request model for creating a Workout record"""


class WorkoutUpdate(WorkoutBase):
    """Request model for updating a Workout record"""

    name: Optional[str] = None


class WorkoutResponse(WorkoutBase):
    """Response model for Workout data"""

    id: int

    class Config:
        from_attributes = True


class WorkoutListResponse(BaseModel):
    """Response model for a list of Workout records"""

    items: List[WorkoutResponse]
    count: int
    total: int
