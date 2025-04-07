from typing import Any, Dict, List
from pydantic import BaseModel, Field


class TrackerBase(BaseModel):
    """Base model for Tracker data"""

    data: Dict[str, Any] = Field(default_factory=dict)


class TrackerCreate(TrackerBase):
    """Request model for creating a Tracker record"""


class TrackerUpdate(TrackerBase):
    """Request model for updating a Tracker record"""


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
