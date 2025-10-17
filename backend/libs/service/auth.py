from datetime import UTC, datetime, timedelta
from typing import Any, Dict, Tuple, Optional, Union

from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from libs import ErrorCode, ExceptionBase, settings
from libs.models.user import User as UserModel


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

    async def create_token(
        self,
        user_id: str,
        username: str,
        email: str,
        expires_minutes: Optional[int] = None,
        check_user: bool = True,
    ) -> Tuple[str, int]:
        # Check if user exists (optional)
        if check_user:
            user = await self.check_user(user_id)
            if not user:
                raise ExceptionBase(ErrorCode.INVALID_CREDENTIALS)

        # Determine expiration time (default 24 hours)
        if expires_minutes is None:
            expires_minutes = self.ACCESS_TOKEN_EXPIRE_MINUTES

        # Create token expiration time
        expires_delta = timedelta(minutes=expires_minutes)
        expire = datetime.now(UTC) + expires_delta

        # Prepare token claims
        claims = {
            "exp": expire,
            "sub": user_id,
            "username": username,
            "email": email,
        }

        # Encode the token
        access_token = jwt.encode(claims, self.SECRET_KEY, algorithm=self.ALGORITHM)

        # Return access token and expiry time in seconds
        return access_token, self.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    async def create_token_pair(
        self, user_id: str, username: str, email: str, check_user: bool = True
    ) -> Tuple[str, int]:
        return await self.create_token(user_id=user_id, username=username, email=email, check_user=check_user)

    async def validate_token(self, token: str) -> Dict[str, Any]:
        return await self._process_token(token, check_user=False)

    async def validate_token_with_user(self, token: str) -> Tuple[Dict[str, Any], UserModel]:
        payload, user = await self._process_token(token, check_user=True)
        return payload, user

    async def get_user_from_token(self, token: str) -> UserModel:
        _, user = await self._process_token(token, check_user=True)
        return user

    async def _process_token(
        self, token: str, check_user: bool = True
    ) -> Union[Dict[str, Any], Tuple[Dict[str, Any], UserModel]]:
        if not token:
            raise ExceptionBase(ErrorCode.UNAUTHORIZED)

        try:
            # Extract token from Authorization header if needed
            if token.lower().startswith("bearer ") and len(token) > 7:
                token = token[7:]

            # Clean token string
            token = token.split(",")[0].strip('"')

            # Decode and verify token
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

            # Ensure user ID is present
            if not payload.get("sub"):
                raise ExceptionBase(ErrorCode.INVALID_TOKEN)

            # Verify user still exists (optional)
            if check_user:
                user = await self.check_user(payload.get("sub"))
                if not user:
                    raise ExceptionBase(ErrorCode.INVALID_TOKEN)
                return payload, user

            return payload

        except JWTError:
            raise ExceptionBase(ErrorCode.INVALID_TOKEN)
        except ValueError:
            raise ExceptionBase(ErrorCode.BAD_REQUEST)

    async def check_user(self, user_id: str) -> Optional[UserModel]:
        try:
            user_id_int = int(user_id)
            result = await self.db.execute(
                select(UserModel).where(
                    UserModel.id == user_id_int, UserModel.is_active == True, UserModel.deleted_date.is_(None)
                )
            )
            return result.scalars().first()
        except (ValueError, TypeError):
            return None
