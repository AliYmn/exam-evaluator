from typing import List, Optional
from pydantic import BaseModel


# WorkoutCategory schemas
class WorkoutCategoryBase(BaseModel):
    """Base model for WorkoutCategory data"""

    name: str
    description: Optional[str] = None


class WorkoutCategoryCreate(WorkoutCategoryBase):
    """Request model for creating a WorkoutCategory"""


class WorkoutCategoryUpdate(BaseModel):
    """Request model for updating a WorkoutCategory"""

    name: Optional[str] = None
    description: Optional[str] = None


class WorkoutCategoryResponse(WorkoutCategoryBase):
    """Response model for WorkoutCategory data"""

    id: int

    class Config:
        from_attributes = True


class WorkoutCategoryListResponse(BaseModel):
    """Response model for a list of WorkoutCategory records"""

    items: List[WorkoutCategoryResponse]
    total: int


# Workout schemas
class WorkoutSetBase(BaseModel):
    """Base model for WorkoutSet data"""

    set_number: int
    reps: Optional[int] = None
    weight: Optional[float] = None
    duration_seconds: Optional[int] = None
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None


class WorkoutSetCreate(WorkoutSetBase):
    """Request model for creating a WorkoutSet"""


class WorkoutSetUpdate(BaseModel):
    """Request model for updating a WorkoutSet"""

    set_number: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    duration_seconds: Optional[int] = None
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None


class WorkoutSetResponse(WorkoutSetBase):
    """Response model for WorkoutSet data"""

    id: int
    workout_id: int

    class Config:
        from_attributes = True


class WorkoutBase(BaseModel):
    """Base model for Workout data"""

    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    difficulty_level: Optional[str] = None
    equipment_needed: Optional[str] = None
    muscle_groups: Optional[str] = None
    instructions: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    is_custom: Optional[int] = 1  # Default to custom workout


class WorkoutCreate(WorkoutBase):
    """Request model for creating a Workout"""

    sets: Optional[List[WorkoutSetCreate]] = None


class WorkoutUpdate(BaseModel):
    """Request model for updating a Workout"""

    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    difficulty_level: Optional[str] = None
    equipment_needed: Optional[str] = None
    muscle_groups: Optional[str] = None
    instructions: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    is_custom: Optional[int] = None


class WorkoutResponse(WorkoutBase):
    """Response model for Workout data"""

    id: int
    user_id: Optional[int] = None
    sets: List[WorkoutSetResponse] = []
    category: Optional[WorkoutCategoryResponse] = None

    class Config:
        from_attributes = True


class WorkoutListResponse(BaseModel):
    """Response model for a list of Workout records"""

    items: List[WorkoutResponse]
    total: int


# WorkoutProgram schemas
class WorkoutProgramDayBase(BaseModel):
    """Base model for WorkoutProgramDay data"""

    day_number: int
    name: str
    description: Optional[str] = None


class WorkoutProgramDayCreate(WorkoutProgramDayBase):
    """Request model for creating a WorkoutProgramDay"""

    workout_ids: List[int] = []


class WorkoutProgramDayUpdate(BaseModel):
    """Request model for updating a WorkoutProgramDay"""

    day_number: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    workout_ids: Optional[List[int]] = None


class WorkoutProgramDayResponse(WorkoutProgramDayBase):
    """Response model for WorkoutProgramDay data"""

    id: int
    program_id: int
    workouts: List[WorkoutResponse] = []

    class Config:
        from_attributes = True


class WorkoutProgramBase(BaseModel):
    """Base model for WorkoutProgram data"""

    name: str
    description: Optional[str] = None
    group_name: Optional[str] = None
    difficulty_level: Optional[str] = None
    duration_weeks: Optional[int] = None
    goal: Optional[str] = None
    is_public: Optional[int] = 0


class WorkoutProgramCreate(WorkoutProgramBase):
    """Request model for creating a WorkoutProgram"""

    days: Optional[List[WorkoutProgramDayCreate]] = None


class WorkoutProgramUpdate(BaseModel):
    """Request model for updating a WorkoutProgram"""

    name: Optional[str] = None
    description: Optional[str] = None
    group_name: Optional[str] = None
    difficulty_level: Optional[str] = None
    duration_weeks: Optional[int] = None
    goal: Optional[str] = None
    is_public: Optional[int] = None


class WorkoutProgramResponse(WorkoutProgramBase):
    """Response model for WorkoutProgram data"""

    id: int
    user_id: int
    days: List[WorkoutProgramDayResponse] = []

    class Config:
        from_attributes = True


class WorkoutProgramListResponse(BaseModel):
    """Response model for a list of WorkoutProgram records"""

    items: List[WorkoutProgramResponse]
    total: int
