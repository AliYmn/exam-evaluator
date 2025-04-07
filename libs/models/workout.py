from sqlalchemy import Column, String, Float, JSON
from libs.models.base import BaseModel


class Workout(BaseModel):
    __tablename__ = "workouts"

    name = Column(String(255), nullable=False, index=True)  # Örn: Bench Press, Squat
    description = Column(String(500), nullable=True)  # Açıklama, not, varyasyon
    workout_type = Column(String(50), nullable=True)  # Örn: strength, cardio, flexibility
    target_muscles = Column(JSON, default=list)  # Örn: ["chest", "triceps"]

    duration_minutes = Column(Float, nullable=True)  # Ortalama süre (örn. 30 dk)
    calories_burned = Column(Float, nullable=True)  # Tahmini yakılan kalori
    equipment = Column(String(100), nullable=True)  # Örn: barbell, dumbbell, yoga mat

    difficulty = Column(String(20), nullable=True)  # Örn: beginner, intermediate, advanced
    instructions = Column(JSON, default=dict)  # Adım adım anlatım, video linkleri, tekrarlar

    def __repr__(self):
        return f"<Workout(name={self.name}, type={self.type})>"
