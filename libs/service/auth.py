from datetime import UTC, datetime, timedelta
from typing import Any, Dict, Tuple

from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from libs import ErrorCode, ExceptionBase, settings


class User(BaseModel):
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

    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate a JWT token"""
        if not token:
            raise ExceptionBase(ErrorCode.UNAUTHORIZED)

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
                raise ExceptionBase(ErrorCode.INVALID_TOKEN)

            return payload
        except JWTError:
            raise ExceptionBase(ErrorCode.INVALID_TOKEN)

    def check_token(self, token: str) -> bool:
        """Simple token validation, returns True if valid or raises an exception"""
        self.decode_token(token)
        return True

    def get_user_from_token(self, token: str) -> User:
        """Extract user information from token"""
        payload = self.decode_token(token)

        return User(
            username=payload.get("username", ""), email=payload.get("email", ""), user_id=payload.get("sub", "")
        )

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
