from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from libs.models.base import BaseModel


class DietTracker(BaseModel):
    __tablename__ = "diet_trackers"

    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    diet_id = Column(Integer, ForeignKey("diets.id"), nullable=False, index=True)
    is_compliant = Column(Boolean, nullable=True)

    def __repr__(self):
        return f"<DietTracker(user_id={self.user_id})>"
