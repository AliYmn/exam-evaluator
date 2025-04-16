from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String

from libs.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    # Authentication and account status (globally unique, not app-specific)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String(50), default="user")

    # Personal information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    profile_picture = Column(String(255), nullable=True)
    gender = Column(String(10), nullable=True)
    height = Column(Integer, nullable=True)
    weight = Column(Integer, nullable=True)
    bmi = Column(Integer, nullable=True)
    body_tracker_period = Column(String(20), default="weekly")
    language = Column(String(10), nullable=True, default="en")
    referral_code = Column(String(50), nullable=True)

    # Location and contact details
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    timezone = Column(String(100), nullable=True)

    # User preferences
    preferences = Column(JSON, default=dict)

    # Security and password reset functionality
    last_login = Column(DateTime, nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)

    # Premium features
    package_type = Column(String(50), default="basic")
    subscription_start = Column(DateTime, nullable=True)
    subscription_end = Column(DateTime, nullable=True)
    billing_period = Column(String(20), default="monthly")
    auto_renew = Column(Boolean, default=False)
    usage_limit = Column(Integer, default=0)
    storage_limit = Column(Integer, default=0)
    package_features = Column(JSON, default=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<User(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}>"
