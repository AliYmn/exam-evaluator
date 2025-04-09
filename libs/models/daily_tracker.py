from sqlalchemy import Column, Integer, ForeignKey, Float, String

from libs.models.base import BaseModel


class DailyTracker(BaseModel):
    __tablename__ = "daily_trackers"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    energy = Column(Integer, nullable=True)
    sleep = Column(Integer, nullable=True)
    stress = Column(Integer, nullable=True)
    muscle_soreness = Column(Integer, nullable=True)
    fatigue = Column(Integer, nullable=True)
    hunger = Column(Integer, nullable=True)
    water_intake_liters = Column(Float, nullable=True)
    sleep_hours = Column(Float, nullable=True)
    mood = Column(String(50), nullable=True)
    bowel_movement = Column(String(50), nullable=True)
    training_quality = Column(Integer, nullable=True)
    diet_compliance = Column(Integer, nullable=True)
    training_compliance = Column(Integer, nullable=True)
    note = Column(String(255), nullable=True)
    ai_content = Column(String(9999), nullable=True)

    def __repr__(self):
        return f"<DailyTracker(user_id={self.user_id})>"
