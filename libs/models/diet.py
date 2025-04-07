from sqlalchemy import Column, ForeignKey, Integer, String, Float, Text, Table, Boolean
from sqlalchemy.orm import relationship

from libs.models.base import BaseModel

# Association table for many-to-many relationship between DietPlan and Food
diet_plan_food = Table(
    "diet_plan_food",
    BaseModel.metadata,
    Column("diet_plan_id", Integer, ForeignKey("diet_plans.id"), primary_key=True),
    Column("food_id", Integer, ForeignKey("foods.id"), primary_key=True),
    Column("meal_type", String(50)),  # breakfast, lunch, dinner, snack
    Column("portion_size", Float),
    Column("portion_unit", String(20)),
    Column("day_number", Integer),
)

# Association table for many-to-many relationship between DietPlan and Supplement
diet_plan_supplement = Table(
    "diet_plan_supplement",
    BaseModel.metadata,
    Column("diet_plan_id", Integer, ForeignKey("diet_plans.id"), primary_key=True),
    Column("supplement_id", Integer, ForeignKey("supplements.id"), primary_key=True),
    Column("dosage", Float),
    Column("dosage_unit", String(20)),
    Column("time_of_day", String(50)),  # morning, afternoon, evening, pre-workout, post-workout
    Column("day_number", Integer),
)


class FoodCategory(BaseModel):
    __tablename__ = "food_categories"

    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    # Relationships
    foods = relationship("Food", back_populates="category")

    def __repr__(self):
        return f"<FoodCategory(id={self.id}, name={self.name})>"


class Food(BaseModel):
    __tablename__ = "foods"

    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("food_categories.id"), nullable=True)
    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)  # in grams
    carbs = Column(Float, nullable=True)  # in grams
    fat = Column(Float, nullable=True)  # in grams
    fiber = Column(Float, nullable=True)  # in grams
    sugar = Column(Float, nullable=True)  # in grams
    serving_size = Column(Float, nullable=True)
    serving_unit = Column(String(20), nullable=True)  # g, ml, oz, etc.
    image_url = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # For custom foods
    is_custom = Column(Integer, default=0)  # 0: system, 1: custom
    # Relationships
    category = relationship("FoodCategory", back_populates="foods")
    diet_plans = relationship("DietPlan", secondary=diet_plan_food, back_populates="foods")

    def __repr__(self):
        return f"<Food(id={self.id}, name={self.name})>"


class SupplementCategory(BaseModel):
    __tablename__ = "supplement_categories"

    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    # Relationships
    supplements = relationship("Supplement", back_populates="category")

    def __repr__(self):
        return f"<SupplementCategory(id={self.id}, name={self.name})>"


class Supplement(BaseModel):
    __tablename__ = "supplements"

    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("supplement_categories.id"), nullable=True)
    brand = Column(String(100), nullable=True)
    recommended_dosage = Column(Float, nullable=True)
    dosage_unit = Column(String(20), nullable=True)  # g, mg, ml, etc.
    benefits = Column(Text, nullable=True)
    side_effects = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # For custom supplements
    is_custom = Column(Integer, default=0)  # 0: system, 1: custom
    # Relationships
    category = relationship("SupplementCategory", back_populates="supplements")
    diet_plans = relationship("DietPlan", secondary=diet_plan_supplement, back_populates="supplements")

    def __repr__(self):
        return f"<Supplement(id={self.id}, name={self.name})>"


class DietPlan(BaseModel):
    __tablename__ = "diet_plans"

    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal = Column(String(100), nullable=True)  # weight loss, muscle gain, maintenance
    duration_days = Column(Integer, nullable=True)
    daily_calories = Column(Float, nullable=True)
    protein_target = Column(Float, nullable=True)  # in grams
    carbs_target = Column(Float, nullable=True)  # in grams
    fat_target = Column(Float, nullable=True)  # in grams
    is_public = Column(Integer, default=0)  # 0: private, 1: public
    # Relationships
    foods = relationship("Food", secondary=diet_plan_food, back_populates="diet_plans")
    supplements = relationship("Supplement", secondary=diet_plan_supplement, back_populates="diet_plans")

    def __repr__(self):
        return f"<DietPlan(id={self.id}, name={self.name}, user_id={self.user_id})>"


class MealTemplate(BaseModel):
    __tablename__ = "meal_templates"

    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meal_type = Column(String(50), nullable=False)  # breakfast, lunch, dinner, snack
    is_favorite = Column(Boolean, default=False)
    # Relationships
    meal_foods = relationship("MealTemplateFood", back_populates="meal_template", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MealTemplate(id={self.id}, name={self.name}, meal_type={self.meal_type})>"


class MealTemplateFood(BaseModel):
    __tablename__ = "meal_template_foods"

    meal_template_id = Column(Integer, ForeignKey("meal_templates.id"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False)
    portion_size = Column(Float, nullable=False)
    portion_unit = Column(String(20), nullable=False)
    # Relationships
    meal_template = relationship("MealTemplate", back_populates="meal_foods")
    food = relationship("Food")

    def __repr__(self):
        return f"<MealTemplateFood(id={self.id}, meal_template_id={self.meal_template_id}, food_id={self.food_id})>"
