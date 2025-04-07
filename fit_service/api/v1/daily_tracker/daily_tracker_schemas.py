from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class DailyTrackerBase(BaseModel):
    """Base model for Daily Tracker data"""

    energy: Optional[int] = Field(None, ge=1, le=10, description="Energy level from 1-10")
    sleep: Optional[int] = Field(None, ge=1, le=10, description="Sleep quality from 1-10")
    stress: Optional[int] = Field(None, ge=1, le=10, description="Stress level from 1-10")
    muscle_soreness: Optional[int] = Field(None, ge=1, le=10, description="Muscle soreness from 1-10")
    fatigue: Optional[int] = Field(None, ge=1, le=10, description="Fatigue level from 1-10")
    hunger: Optional[int] = Field(None, ge=1, le=10, description="Hunger level from 1-10")
    water_intake_liters: Optional[float] = None
    sleep_hours: Optional[float] = None
    mood: Optional[str] = None


class DailyTrackerCreate(DailyTrackerBase):
    """Request model for creating a Daily Tracker record"""


class DailyTrackerUpdate(DailyTrackerBase):
    """Request model for updating a Daily Tracker record"""


class DailyTrackerResponse(DailyTrackerBase):
    """Response model for Daily Tracker data"""

    id: int
    user_id: int
    created_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class DailyTrackerListResponse(BaseModel):
    """Response model for a list of Daily Tracker records"""

    items: List[DailyTrackerResponse]
    count: int
    total: int
