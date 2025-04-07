from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DietBase(BaseModel):
    """Base model for Diet data"""

    data: Dict[str, Any] = Field(default_factory=dict)


class DietCreate(DietBase):
    """Request model for creating a Diet record"""


class DietUpdate(DietBase):
    """Request model for updating a Diet record"""


class DietResponse(DietBase):
    """Response model for Diet data"""

    id: int
    user_id: int

    class Config:
        from_attributes = True


class DietListResponse(BaseModel):
    """Response model for a list of Diet records"""

    items: List[DietResponse]
    total: int
    count: int


# Diet Tracker schemas
class DietTrackerBase(BaseModel):
    """Base model for Diet Tracker data"""

    name: str
    diet_id: int
    is_compliant: Optional[bool] = None


class DietTrackerCreate(DietTrackerBase):
    """Request model for creating a Diet Tracker record"""


class DietTrackerResponse(DietTrackerBase):
    """Response model for Diet Tracker data"""

    id: int
    user_id: int

    class Config:
        from_attributes = True


class DietTrackerListResponse(BaseModel):
    """Response model for a list of Diet Tracker records"""

    items: List[DietTrackerResponse]
    total: int
    count: int
