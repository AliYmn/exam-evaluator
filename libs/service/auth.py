from typing import Any, Dict, Optional, Tuple

from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from libs import ErrorCode, ExceptionBase, settings
from libs.models import App


class User(BaseModel):
    username: str
    user_id: str
    email: str
    app_name: str
    app_id: Optional[int] = None


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _process_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        if not token:
            return False, None

        try:
            # Handle token prefix if present
            if token.lower().startswith("token ") and len(token) > 7:
                token = token[7:]

            # Clean the token to handle potential malformed input
            token = token.split(",")[0].strip('"')

            # Decode the token
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

            # Validate required claims
            if not payload.get("sub"):
                return False, None

            return True, payload

        except JWTError:
            return False, None

    async def check_token(self, token: str) -> bool:
        is_valid, _ = await self._process_token(token)

        if not is_valid:
            raise ExceptionBase(ErrorCode.INVALID_TOKEN)

        return True

    async def check_app(self, app_name: str) -> int:
        app = await self.db.execute(select(App.id).where(App.name == app_name))
        result = app.scalar()
        if not result:
            raise ExceptionBase(ErrorCode.UNAUTHORIZED)
        return result

    async def decode_token(self, token: str) -> User:
        if not token:
            raise ExceptionBase(ErrorCode.UNAUTHORIZED)

        is_valid, payload = await self._process_token(token)

        if not is_valid:
            raise ExceptionBase(ErrorCode.INVALID_TOKEN)

        app_id = await self.check_app(payload.get("app_name"))
        return User(
            app_name=payload.get("app_name", ""),
            username=payload.get("sub", ""),
            email=payload.get("email", ""),
            user_id=payload.get("user_id", ""),
            app_id=app_id,
        )
