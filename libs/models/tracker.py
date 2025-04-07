from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from libs.models.base import BaseModel


class Tracker(BaseModel):
    __tablename__ = "trackers"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    data = Column(JSON, default=dict, nullable=False)
    user = relationship("User", backref="trackers")

    def __repr__(self):
        return f"<Tracker(user_id={self.user_id})>"
