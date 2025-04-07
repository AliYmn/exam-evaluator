from sqlalchemy import Column, String, Float, JSON
from libs.models.base import BaseModel


class Food(BaseModel):
    __tablename__ = "foods"

    name = Column(String(255), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)
    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    fiber = Column(Float, nullable=True)
    sugar = Column(Float, nullable=True)
    extra = Column(JSON, default=dict)

    def __repr__(self):
        return f"<Food(name={self.name}, calories={self.calories})>"
