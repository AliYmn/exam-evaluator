from datetime import UTC, datetime
from typing import Optional, Literal

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.api.v1.auth.auth_schemas import (
    LoginRequest,
    Token,
    UserCreate,
    UserResponse,
)
from libs import ErrorCode, ExceptionBase
from libs.models.user import User
from libs.service.auth import AuthService as SharedAuthService


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pwd_context = CryptContext(
            schemes=["argon2"],
            argon2__time_cost=2,
            argon2__memory_cost=102400,
            argon2__parallelism=8,
        )
        self.auth_service = SharedAuthService(db)

    async def get_user(self, value: str, field: Literal["email", "id"] = "email") -> Optional[User]:
        if field == "email":
            result = await self.db.execute(
                select(User).where(User.email == value, User.is_active == True, User.deleted_date.is_(None))
            )
        elif field == "id":
            result = await self.db.execute(
                select(User).where(User.id == int(value), User.is_active == True, User.deleted_date.is_(None))
            )

        return result.scalars().first()

    async def create_user(self, user_data: UserCreate) -> None:
        # Check if email already exists
        email_exists = await self.get_user(user_data.email, "email")

        # Return error if email exists
        if email_exists:
            raise ExceptionBase(ErrorCode.DUPLICATE_ENTRY)

        # Create user
        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["password_hash"] = self.pwd_context.hash(user_data.password)
        new_user = User(**user_dict)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

    async def authenticate_user_by_email(self, login_data: LoginRequest) -> Token:
        # Get and validate user
        user = await self.get_user(login_data.email, "email")
        if not user or not self.pwd_context.verify(login_data.password, user.password_hash):
            raise ExceptionBase(ErrorCode.INVALID_CREDENTIALS)

        # Update last login time
        user.last_login = datetime.now(UTC).replace(tzinfo=None)
        await self.db.commit()

        # Generate token - we already validated the user so skip validation in shared service
        access_token, expires_in = await self.auth_service.create_token_pair(
            user_id=str(user.id),
            username=f"{user.first_name} {user.last_name}",
            email=user.email,
            check_user=False,  # Skip redundant user check
        )

        # Return token with user info (24 hours expiry)
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            email=user.email,
            user=UserResponse.model_validate(user),
        )

    async def get_current_user(self, token: str) -> UserResponse:
        # Validate token and get user
        _, user = await self.auth_service.validate_token_with_user(token)

        if not user:
            raise ExceptionBase(ErrorCode.USER_NOT_FOUND)

        # Return user response
        return UserResponse.model_validate(user)

    async def update_user_profile(self, user_id: str, update_data: dict) -> UserResponse:
        # Get user and validate existence
        user = await self.get_user(user_id, "id")
        if not user:
            raise ExceptionBase(ErrorCode.USER_NOT_FOUND)

        # Apply updates
        for field, value in update_data.items():
            setattr(user, field, value)

        # Save changes
        await self.db.commit()
        await self.db.refresh(user)

        return UserResponse.model_validate(user)
