from sqlalchemy import Column, Integer, Float, ForeignKey, String
from libs.models.base import BaseModel


class BodyTracker(BaseModel):
    __tablename__ = "body_trackers"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    weight = Column(Float, nullable=True)
    neck = Column(Float, nullable=True)
    waist = Column(Float, nullable=True)
    shoulder = Column(Float, nullable=True)
    chest = Column(Float, nullable=True)
    hip = Column(Float, nullable=True)
    thigh = Column(Float, nullable=True)
    arm = Column(Float, nullable=True)
    note = Column(String(255), nullable=True)
    ai_content = Column(String(9999), nullable=True)

    def __repr__(self):
        return f"<BodyTracker(user_id={self.user_id})>"
