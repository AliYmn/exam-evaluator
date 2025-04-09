from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Time

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
    fasting_type = Column(String(50), nullable=False)  # e.g., "16:8", "18:6", "20:4", "OMAD"
    is_active = Column(Boolean, default=True)  # Whether this plan is currently active

    # Nutritional targets
    target_calories = Column(Integer, nullable=True)  # Daily calorie target during eating window
    target_meals = Column(Integer, nullable=True)  # Target number of meals during eating window
    target_water = Column(Float, nullable=True)  # Target water intake in liters

    def __repr__(self):
        return f"<FastingPlan(id={self.id}, user_id={self.user_id}, fasting_type={self.fasting_type})>"


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
    status = Column(String(20), default="active")  # active, completed, broken, skipped, failed etc.

    def __repr__(self):
        return f"<FastingSession(id={self.id}, user_id={self.user_id}, status={self.status})>"
