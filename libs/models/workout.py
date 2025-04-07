from sqlalchemy import Column, String, Float, JSON
from libs.models.base import BaseModel


class Workout(BaseModel):
    __tablename__ = "workouts"

    name = Column(String(255), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    workout_type = Column(String(50), nullable=True)
    target_muscles = Column(JSON, default=list)

    duration_minutes = Column(Float, nullable=True)
    calories_burned = Column(Float, nullable=True)
    equipment = Column(String(100), nullable=True)

    difficulty = Column(String(20), nullable=True)
    instructions = Column(JSON, default=dict)

    def __repr__(self):
        return f"<Workout(name={self.name}, type={self.type})>"
