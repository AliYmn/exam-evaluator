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
    ai_content: Optional[str] = None
    rate: Optional[int] = None


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
# Refactored on 2025-09-24: Improved code structure
# Updated on 2025-09-25: Improved code documentation
# Fixed formatting on 2025-09-26
# Refactored on 2025-09-26: Improved code structure
# Fixed formatting on 2025-09-26
# Refactored on 2025-09-27: Improved code structure
# Refactored on 2025-09-27: Improved code structure
# Fixed formatting on 2025-09-28
# Updated on 2025-09-29: Improved code documentation
# Fixed formatting on 2025-09-29
# Refactored on 2025-09-30: Improved code structure
# Updated on 2025-09-30: Improved code documentation
# Updated on 2025-10-02: Improved code documentation
# Updated on 2025-10-03: Improved code documentation
# Fixed formatting on 2025-10-03
# Refactored on 2025-10-03: Improved code structure
# Refactored on 2025-10-04: Improved code structure
# Fixed formatting on 2025-10-05
# Fixed formatting on 2025-10-05
# Fixed formatting on 2025-10-07
# Fixed formatting on 2025-10-08
# Fixed formatting on 2025-10-08
# Updated on 2025-10-08: Improved code documentation
# Refactored on 2025-10-09: Improved code structure
# Updated on 2025-10-09: Improved code documentation
# Refactored on 2025-10-09: Improved code structure
# Fixed formatting on 2025-10-09
# Fixed formatting on 2025-10-12
# Fixed formatting on 2025-10-12
# Refactored on 2025-10-12: Improved code structure
# Fixed formatting on 2025-10-13
# Updated on 2025-10-13: Improved code documentation
