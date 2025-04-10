from sqlalchemy import Column, Integer, String, Float, ForeignKey, Time, JSON, DateTime

from libs.models.base import BaseModel


class FastingPlan(BaseModel):
    """
    Model for user's intermittent fasting plans
    Tracks fasting schedule, calorie targets, meal counts, and other related metrics
    """

    __tablename__ = "fasting_plans"

    # Relationship to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Fasting schedule information
    fasting_hours = Column(Integer, nullable=True)  # Number of hours to fast
    eating_hours = Column(Integer, nullable=True)  # Number of hours to eat
    target_week = Column(Integer, nullable=True)  # Target number of weeks for this fasting plan
    current_week = Column(Float, nullable=True, default=0)  # Current week of the fasting plan
    status = Column(String(20), default="inactive")  # active, completed, broken, skipped, failed etc.

    # Target start and finish dates
    start_date = Column(DateTime, nullable=True)  # Target start date and time for this fasting plan
    finish_date = Column(DateTime, nullable=True)  # Target finish date and time for this fasting plan
    renewal_date = Column(DateTime, nullable=True)  # Target renewal date and time for this fasting plan

    def __repr__(self):
        return f"<FastingPlan(id={self.id}, user_id={self.user_id}, fasting_hours={self.fasting_hours}, eating_hours={self.eating_hours})>"


class FastingSession(BaseModel):
    """
    Model for tracking individual fasting sessions
    Records actual fasting periods, compliance, and metrics for each session
    """

    __tablename__ = "fasting_sessions"

    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("fasting_plans.id"), nullable=True)

    # Session timing
    start_time = Column(Time, nullable=False)  # When this fasting session started
    end_time = Column(Time, nullable=True)  # When this fasting session ended (null if ongoing)

    # Session status
    status = Column(String(20), default="inactive")  # active, completed, broken, skipped, failed etc.

    # Fasting metrics
    fasting_hours = Column(Integer, nullable=True)  # Number of hours fasted
    eating_hours = Column(Integer, nullable=True)  # Number of hours eating
    target_week = Column(Integer, nullable=True)  # Target number of weeks for this fasting session
    current_week = Column(Float, nullable=True)  # Current week of the fasting session

    # Nutritional targets
    target_calories = Column(Integer, nullable=True)  # Daily calorie target during eating window
    target_meals = Column(Integer, nullable=True)  # Target number of meals during eating window
    target_water = Column(Float, nullable=True)  # Target water intake in liters
    target_protein = Column(Float, nullable=True)  # Target protein intake in grams
    target_carb = Column(Float, nullable=True)  # Target carbohydrate intake in grams
    target_fat = Column(Float, nullable=True)  # Target fat intake in grams

    # User feedback
    mood = Column(String(50), nullable=True)  # User's mood during fasting (can store emoji)
    stage = Column(String(50), nullable=True)  # Fasting stage (e.g., "anabolic", "catabolic", "ketosis")

    def __repr__(self):
        return f"<FastingSession(id={self.id}, user_id={self.user_id}, status={self.status})>"


class FastingMealLog(BaseModel):
    """
    Model for logging meals during fasting eating windows
    Allows users to track what they eat with photos and notes
    """

    __tablename__ = "fasting_meal_logs"

    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("fasting_sessions.id"), nullable=False, index=True)

    # Meal content
    photo_url = Column(String(255), nullable=True)  # URL to the uploaded photo
    notes = Column(String(500), nullable=True)  # User notes about the meal

    # Nutritional information
    calories = Column(Integer, nullable=True)  # Estimated calories
    protein = Column(Float, nullable=True)  # Protein in grams
    carbs = Column(Float, nullable=True)  # Carbohydrates in grams
    fat = Column(Float, nullable=True)  # Fat in grams

    # Detailed macro data
    detailed_macros = Column(JSON, nullable=True)  # Detailed breakdown of nutrients in JSON format

    # AI generated data
    ai_content = Column(String(9999), nullable=True)

    def __repr__(self):
        return f"<FastingMealLog(id={self.id}, user_id={self.user_id}, session_id={self.session_id})>"


class FastingWorkoutLog(BaseModel):
    """
    Model for logging workouts during fasting periods
    Tracks workout details, duration, and calories burned
    """

    __tablename__ = "fasting_workout_logs"

    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("fasting_sessions.id"), nullable=False, index=True)

    # Workout details
    workout_name = Column(String(100), nullable=False)  # Name of the workout
    duration_minutes = Column(Integer, nullable=True)  # Duration in minutes
    calories_burned = Column(Integer, nullable=True)  # Estimated calories burned

    # Optional workout details
    intensity = Column(String(50), nullable=True)  # Low, Medium, High
    notes = Column(String(500), nullable=True)  # User notes about the workout

    def __repr__(self):
        return f"<FastingWorkoutLog(id={self.id}, user_id={self.user_id}, workout_name={self.workout_name})>"
