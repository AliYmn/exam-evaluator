from sqlalchemy import Column, ForeignKey, Integer, String, Float, Text, Table
from sqlalchemy.orm import relationship

from libs.models.base import BaseModel

# Association table for many-to-many relationship between WorkoutProgramDay and Workout
workout_program_day_workout = Table(
    "workout_program_day_workout",
    BaseModel.metadata,
    Column("workout_program_day_id", Integer, ForeignKey("workout_program_days.id"), primary_key=True),
    Column("workout_id", Integer, ForeignKey("workouts.id"), primary_key=True),
)


class WorkoutCategory(BaseModel):
    __tablename__ = "workout_categories"
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    # Relationships
    workouts = relationship("Workout", back_populates="category")

    def __repr__(self):
        return f"<WorkoutCategory(id={self.id}, name={self.name})>"


class Workout(BaseModel):
    __tablename__ = "workouts"
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("workout_categories.id"), nullable=True)
    difficulty_level = Column(String(20), nullable=True)  # beginner, intermediate, advanced
    equipment_needed = Column(String(255), nullable=True)
    muscle_groups = Column(String(255), nullable=True)
    instructions = Column(Text, nullable=True)
    video_url = Column(String(255), nullable=True)
    image_url = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # For custom workouts
    is_custom = Column(Integer, default=0)  # 0: system, 1: custom
    # Relationships
    category = relationship("WorkoutCategory", back_populates="workouts")
    sets = relationship("WorkoutSet", back_populates="workout", cascade="all, delete-orphan")
    program_days = relationship("WorkoutProgramDay", secondary=workout_program_day_workout, back_populates="workouts")

    def __repr__(self):
        return f"<Workout(id={self.id}, name={self.name})>"


class WorkoutSet(BaseModel):
    __tablename__ = "workout_sets"
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    set_number = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    rest_seconds = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    # Relationships
    workout = relationship("Workout", back_populates="sets")

    def __repr__(self):
        return f"<WorkoutSet(id={self.id}, workout_id={self.workout_id}, set_number={self.set_number})>"


class WorkoutProgram(BaseModel):
    __tablename__ = "workout_programs"
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_name = Column(String(100), nullable=True, index=True)
    difficulty_level = Column(String(20), nullable=True)
    duration_weeks = Column(Integer, nullable=True)
    goal = Column(String(100), nullable=True)
    is_public = Column(Integer, default=0)  # 0: private, 1: public
    # Relationships
    days = relationship("WorkoutProgramDay", back_populates="program", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WorkoutProgram(id={self.id}, name={self.name}, user_id={self.user_id})>"


class WorkoutProgramDay(BaseModel):
    __tablename__ = "workout_program_days"
    program_id = Column(Integer, ForeignKey("workout_programs.id"), nullable=False)
    day_number = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)  # e.g., "Push Day", "Leg Day", "Day 1", etc.
    description = Column(Text, nullable=True)
    # Relationships
    program = relationship("WorkoutProgram", back_populates="days")
    workouts = relationship("Workout", secondary=workout_program_day_workout, back_populates="program_days")

    def __repr__(self):
        return f"<WorkoutProgramDay(id={self.id}, program_id={self.program_id}, name={self.name})>"
