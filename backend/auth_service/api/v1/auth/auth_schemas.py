import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from libs import ErrorCode, ExceptionBase


def validate_strong_password(password: str) -> str:
    """Validate password strength"""
    # Length check
    if len(password) < 6:
        raise ExceptionBase(ErrorCode.WEAK_PASSWORD)

    return password


def validate_email_format(email: str) -> str:
    """Extended email validation"""
    # Basic format
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_regex, email):
        raise ExceptionBase(ErrorCode.INVALID_EMAIL)

    # Additional checks
    if ".." in email:
        raise ExceptionBase(ErrorCode.INVALID_EMAIL)
    if len(email) > 255:
        raise ExceptionBase(ErrorCode.INVALID_EMAIL)

    # Part lengths
    local_part, domain = email.split("@")
    if len(local_part) > 64:
        raise ExceptionBase(ErrorCode.INVALID_EMAIL)

    return email


class LoginRequest(BaseModel):
    """Login request model for authentication"""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    email: EmailStr


class UserCreate(BaseModel):
    """User creation model for registration"""

    email: EmailStr
    password: str
    first_name: str
    last_name: str

    @field_validator("password", mode="before")
    def validate_password(cls, v):
        return validate_strong_password(v)

    @field_validator("email", mode="before")
    def validate_email(cls, v):
        return validate_email_format(v)


class UserUpdate(BaseModel):
    """Model for updating user profile data"""

    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserResponse(BaseModel):
    """Response model for user profile data"""

    id: int
    email: EmailStr
    is_active: bool
    role: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True
