from typing import List, Optional
from datetime import date
from pydantic import BaseModel


class TrackerBase(BaseModel):
    """Base model for Tracker data"""

    weight: Optional[float] = None
    neck: Optional[float] = None
    waist: Optional[float] = None
    shoulder: Optional[float] = None
    chest: Optional[float] = None
    hip: Optional[float] = None
    thigh: Optional[float] = None
    arm: Optional[float] = None


class TrackerCreate(TrackerBase):
    """Request model for creating a Tracker record"""


class TrackerUpdate(TrackerBase):
    """Request model for updating a Tracker record"""

    date: Optional[date] = None


class TrackerResponse(TrackerBase):
    """Response model for Tracker data"""

    id: int
    user_id: int

    class Config:
        from_attributes = True


class TrackerListResponse(BaseModel):
    """Response model for a list of Tracker records"""

    items: List[TrackerResponse]
    total: int
