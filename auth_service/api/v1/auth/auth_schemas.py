import re
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr, field_validator

from libs import ErrorCode, ExceptionBase


def to_naive_datetime(dt: datetime) -> datetime:
    """Convert datetime to naive (no timezone)"""

    if dt and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def validate_strong_password(password: str) -> str:
    """Validate password strength"""

    # Length check
    if len(password) < 8:
        raise ExceptionBase(ErrorCode.WEAK_PASSWORD)

    # Character type checks
    if not re.search(r"[A-Z]", password):
        raise ExceptionBase(ErrorCode.WEAK_PASSWORD)
    if not re.search(r"[a-z]", password):
        raise ExceptionBase(ErrorCode.WEAK_PASSWORD)
    if not re.search(r"\d", password):
        raise ExceptionBase(ErrorCode.WEAK_PASSWORD)
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
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


def validate_phone_number(phone: str) -> str:
    """Validate phone number format"""

    if not phone:
        return phone

    # Remove spaces
    phone = phone.strip()

    # Length check
    if len(phone) > 20:
        raise ExceptionBase(ErrorCode.INVALID_PHONE_NUMBER)

    # Format check
    phone_pattern = r"^(\+?\d{1,3})?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$"
    if not re.match(phone_pattern, phone):
        raise ExceptionBase(ErrorCode.INVALID_PHONE_NUMBER)

    return phone


class LoginRequest(BaseModel):
    """Login request model for authentication"""

    email: EmailStr
    password: str
    grant_type: Optional[str] = "password"
    scope: Optional[str] = ""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None


class RefreshToken(BaseModel):
    """Refresh token request model"""

    refresh_token: str


class PasswordReset(BaseModel):
    """Password reset request model"""

    email: EmailStr


class NewPassword(BaseModel):
    """New password model for reset requests"""

    password: str

    @field_validator("password", mode="before")
    def validate_password(cls, v):
        return validate_strong_password(v)


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    email: EmailStr


class UserCreate(BaseModel):
    """User creation model with full profile data"""

    email: EmailStr
    password: str
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None
    profile_picture: Optional[str] = None
    gender: Optional[str] = None
    language: Optional[str] = None
    referral_code: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    timezone: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    package_type: Optional[str] = None

    @field_validator("date_of_birth", mode="after")
    def validate_date_of_birth(cls, v):
        if v:
            return to_naive_datetime(v)
        return v

    @field_validator("password", mode="before")
    def validate_password(cls, v):
        return validate_strong_password(v)

    @field_validator("email", mode="before")
    def validate_email(cls, v):
        return validate_email_format(v)

    @field_validator("phone_number", mode="before")
    def validate_phone(cls, v):
        if v:
            return validate_phone_number(v)
        return v


class UserUpdate(BaseModel):
    """Model for updating user profile data"""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    profile_picture: Optional[str] = None
    gender: Optional[str] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    body_tracker_period: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    timezone: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

    @field_validator("phone_number")
    def validate_phone(cls, v):
        if v:
            return validate_phone_number(v)
        return v


class UserResponse(BaseModel):
    """Response model for user profile data"""

    id: int
    email: EmailStr
    is_active: bool
    is_verified: Optional[bool] = None
    role: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    profile_picture: Optional[str] = None
    gender: Optional[str] = None
    language: Optional[str] = None
    referral_code: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    timezone: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    last_login: Optional[datetime] = None
    reset_token: Optional[str] = None
    reset_token_expiry: Optional[datetime] = None
    package_type: Optional[str] = None
    subscription_start: Optional[datetime] = None
    subscription_end: Optional[datetime] = None
    billing_period: Optional[str] = None
    auto_renew: Optional[bool] = None
    usage_limit: Optional[int] = None
    storage_limit: Optional[int] = None
    package_features: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

    @field_validator(
        "date_of_birth",
        "last_login",
        "reset_token_expiry",
        "subscription_start",
        "subscription_end",
        mode="after",
    )
    def validate_datetimes(cls, v):
        if v:
            return to_naive_datetime(v)
        return v
# Fixed formatting on 2025-08-09
# Fixed formatting on 2025-08-10
# Fixed formatting on 2025-08-10
# Refactored on 2025-08-11: Improved code structure
# Refactored on 2025-08-11: Improved code structure
