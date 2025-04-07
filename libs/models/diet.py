from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from libs.models.base import BaseModel


class Diet(BaseModel):
    __tablename__ = "diets"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    data = Column(JSON, default=dict, nullable=False)

    user = relationship("User", backref="diets")

    def __repr__(self):
        return f"<Diet(user_id={self.user_id})>"
