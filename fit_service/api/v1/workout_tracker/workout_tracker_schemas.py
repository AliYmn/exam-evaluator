from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class WorkoutTrackerBase(BaseModel):
    """Base model for Workout Tracker data"""

    name: str
    workout_id: int
    is_completed: Optional[bool] = False
    duration_minutes: Optional[int] = None
    calories_burned: Optional[int] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    notes: Optional[str] = None
    custom_data: Optional[dict] = Field(default_factory=dict)


class WorkoutTrackerCreate(WorkoutTrackerBase):
    """Request model for creating a Workout Tracker record"""


class WorkoutTrackerUpdate(WorkoutTrackerBase):
    """Request model for updating a Workout Tracker record"""

    name: Optional[str] = None
    workout_id: Optional[int] = None


class WorkoutTrackerResponse(WorkoutTrackerBase):
    """Response model for Workout Tracker data"""

    id: int
    user_id: int
    created_date: datetime

    class Config:
        from_attributes = True


class WorkoutTrackerListResponse(BaseModel):
    """Response model for a list of Workout Tracker records"""

    items: List[WorkoutTrackerResponse]
    count: int
    total: int
