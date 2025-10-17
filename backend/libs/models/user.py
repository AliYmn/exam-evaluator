from sqlalchemy import Boolean, Column, DateTime, String

from libs.models.base import BaseModel


class User(BaseModel):
    """Minimal user model for exam evaluator authentication"""

    __tablename__ = "users"

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default="user")

    # Basic user info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    last_login = Column(DateTime, nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<User(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email})>"
