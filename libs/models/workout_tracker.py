from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Boolean
from libs.models.base import BaseModel


class WorkoutTracker(BaseModel):
    __tablename__ = "workout_trackers"

    name = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False, index=True)
    is_completed = Column(Boolean, default=False)

    # Performance metrics
    duration_minutes = Column(Integer, nullable=True)
    calories_burned = Column(Integer, nullable=True)

    # Program details
    sets = Column(Integer, nullable=True)
    reps = Column(Integer, nullable=True)

    # Additional data
    notes = Column(String(500), nullable=True)
    custom_data = Column(JSON, default=dict)

    def __repr__(self):
        return f"<WorkoutTracker(user_id={self.user_id}, workout_id={self.workout_id})>"
