from datetime import UTC, datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from libs import ErrorCode, ExceptionBase, settings


class TokenUser(BaseModel):
    username: str
    user_id: str
    email: str


class AuthService:
    def __init__(self, db: AsyncSession = None):
        self.db = db
        self.SECRET_KEY = settings.JWT_SECRET_KEY
        self.ALGORITHM = settings.JWT_ALGORITHM
        self.ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.REFRESH_TOKEN_EXPIRE_DAYS = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS

    def create_token(
        self, user_id: str, username: str, email: str, expires_minutes: int = None, is_refresh_token: bool = False
    ) -> str:
        """Create a JWT token with user information"""
        if expires_minutes is None:
            expires_minutes = (
                self.ACCESS_TOKEN_EXPIRE_MINUTES if not is_refresh_token else self.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60
            )

        expires_delta = timedelta(minutes=expires_minutes)
        expire = datetime.now(UTC) + expires_delta

        claims = {
            "exp": expire,
            "sub": user_id,
            "username": username,
            "email": email,
        }

        # Add refresh token flag if needed
        if is_refresh_token:
            claims["token_type"] = "refresh"

        return jwt.encode(claims, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def create_token_pair(self, user_id: str, username: str, email: str) -> Tuple[str, str, int]:
        """Create an access and refresh token pair"""
        # Access token
        access_token = self.create_token(user_id=user_id, username=username, email=email)

        # Refresh token
        refresh_token = self.create_token(
            user_id=user_id,
            username=username,
            email=email,
            is_refresh_token=True,
            expires_minutes=self.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60,  # Convert days to minutes
        )

        return access_token, refresh_token, self.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Return expiry in seconds

    async def validate_token(self, token: str, check_user: bool = True) -> Tuple[Dict[str, Any], Optional[Any]]:
        """
        Comprehensive token validation that:
        1. Validates JWT token integrity and expiration
        2. Optionally verifies the user exists in the database and is active

        Returns a tuple of (token_payload, user_record)
        If check_user is False, user_record will be None

        Raises exceptions for invalid tokens or non-existent/inactive users
        """
        if not token:
            raise ExceptionBase(ErrorCode.UNAUTHORIZED, "Token is missing")

        try:
            # Handle token prefix if present
            if token.lower().startswith("bearer ") and len(token) > 7:
                token = token[7:]

            # Clean the token to handle potential malformed input
            token = token.split(",")[0].strip('"')

            # Decode the token
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

            # Validate required claims
            if not payload.get("sub"):
                raise ExceptionBase(ErrorCode.INVALID_TOKEN, "Invalid token claims")

            # If user validation is requested
            user = None
            if check_user:
                if not self.db:
                    raise ValueError("Database session is required for user validation")

                # Get user from database
                from libs.models.user import User as UserModel

                user_id = int(payload.get("sub"))
                result = await self.db.execute(
                    select(UserModel).where(UserModel.id == user_id, UserModel.deleted_date is None)
                )
                user = result.scalars().first()

                # Verify user exists and is active
                if not user:
                    raise ExceptionBase(ErrorCode.NOT_FOUND, "User not found")

                if not user.is_active:
                    raise ExceptionBase(ErrorCode.UNAUTHORIZED, "User account is inactive")

            return payload, user

        except JWTError:
            raise ExceptionBase(ErrorCode.INVALID_TOKEN, "Invalid or expired token")
        except ValueError as e:
            raise ExceptionBase(ErrorCode.BAD_REQUEST, str(e))

    async def get_user_by_id(self, user_id: int):
        """Get a user by ID"""
        from libs.models.user import User as UserModel

        if not self.db:
            raise ValueError("Database session is required for this operation")

        result = await self.db.execute(select(UserModel).where(UserModel.id == user_id))
        return result.scalars().first()
