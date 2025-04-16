import secrets
from datetime import UTC, datetime, timedelta
from typing import Optional, Literal, Union

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.api.v1.auth.auth_schemas import (
    LoginRequest,
    PasswordReset,
    RefreshToken,
    Token,
    UserCreate,
    UserResponse,
    UserUpdate,
    to_naive_datetime,
)
from auth_service.core.worker.tasks import (
    send_password_changed_email_task,
    send_password_reset_email_task,
    send_welcome_email_task,
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

        # Send welcome email
        send_welcome_email_task.delay(to_email=new_user.email, first_name=new_user.first_name)

    async def authenticate_user_by_email(self, login_data: LoginRequest) -> Token:
        # Get and validate user
        user = await self.get_user(login_data.email, "email")
        if not user or not self.pwd_context.verify(login_data.password, user.password_hash):
            raise ExceptionBase(ErrorCode.INVALID_CREDENTIALS)

        # Update last login time
        user.last_login = datetime.now(UTC).replace(tzinfo=None)
        await self.db.commit()

        # Generate tokens - we already validated the user so skip validation in shared service
        access_token, refresh_token, expires_in = await self.auth_service.create_token_pair(
            user_id=str(user.id),
            username=f"{user.first_name} {user.last_name}",
            email=user.email,
            check_user=False,  # Skip redundant user check
        )

        # Return token
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
            email=user.email,
        )

    async def refresh_token(self, refresh_token_data: RefreshToken) -> Token:
        # Validate refresh token - don't check user in database since we'll do it ourselves
        payload = await self.auth_service.validate_token(refresh_token_data.refresh_token)

        # Check token type
        if "token_type" not in payload or payload["token_type"] != "refresh":
            raise ExceptionBase(ErrorCode.INVALID_TOKEN)

        # Get user from token
        user_id = payload.get("sub")
        if not user_id:
            raise ExceptionBase(ErrorCode.INVALID_TOKEN)

        # Get user by ID
        user = await self.get_user(user_id, "id")
        if not user:
            raise ExceptionBase(ErrorCode.USER_NOT_FOUND)

        # Generate new tokens - we already validated the user so skip validation in shared service
        access_token, refresh_token, expires_in = await self.auth_service.create_token_pair(
            user_id=str(user.id),
            username=f"{user.first_name} {user.last_name}",
            email=user.email,
            check_user=False,  # Skip redundant user check
        )

        # Return token
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            refresh_token=refresh_token,
            email=user.email,
        )

    async def get_current_user(self, token: str) -> UserResponse:
        # Validate token and get user
        _, user = await self.auth_service.validate_token_with_user(token)

        if not user:
            raise ExceptionBase(ErrorCode.USER_NOT_FOUND)

        # Return user response
        return UserResponse.model_validate(user)

    async def update_user_profile(self, user_id: str, update_data: Union[UserUpdate, dict]) -> UserResponse:
        # Get user and validate existence
        user = await self.get_user(user_id, "id")
        if not user:
            raise ExceptionBase(ErrorCode.USER_NOT_FOUND)

        # Apply updates from validated schema and calculate BMI
        if hasattr(update_data, "model_dump"):
            # If it's a Pydantic model
            user_data = update_data.model_dump(exclude_unset=True)
        else:
            # If it's a dictionary
            user_data = update_data

        for field, value in user_data.items():
            setattr(user, field, value)

        # Auto-calculate BMI when height and weight are available
        if user.height and user.weight:
            user.bmi = self.calculate_bmi(user.height, user.weight)

        # Save changes
        await self.db.commit()
        await self.db.refresh(user)

        return UserResponse.model_validate(user)

    def calculate_bmi(self, height: int, weight: int) -> int:
        """
        Calculate BMI (Body Mass Index) using height in cm and weight in kg.
        Formula: BMI = weight(kg) / (height(m))²
        Returns BMI as an integer.
        """
        if height <= 0 or weight <= 0:
            return 0

        # Convert height from cm to meters
        height_in_meters = height / 100

        # Calculate BMI
        bmi = weight / (height_in_meters * height_in_meters)

        # Return as integer
        return int(round(bmi))

    async def request_password_reset(self, email_data: PasswordReset) -> None:
        # Get user by email
        user = await self.get_user(email_data.email, "email")
        if not user:
            return  # Silently return for security

        # Generate 6-digit reset token
        reset_token = "".join(secrets.choice("0123456789") for _ in range(6))
        user.reset_token = reset_token
        user.reset_token_expiry = to_naive_datetime(datetime.now(UTC) + timedelta(hours=24))
        await self.db.commit()

        # Send reset email
        send_password_reset_email_task.delay(to_email=user.email, first_name=user.first_name, reset_token=reset_token)

    async def reset_password(self, reset_token: str, new_password: str) -> None:
        # Validate reset token
        now = to_naive_datetime(datetime.now(UTC))
        result = await self.db.execute(
            select(User).where(
                User.reset_token == reset_token,
                User.reset_token_expiry > now,
                User.is_active == True,
                User.deleted_date.is_(None),
            )
        )
        user = result.scalars().first()
        if not user:
            raise ExceptionBase(ErrorCode.INVALID_RESET_TOKEN)

        # Update password
        user.password_hash = self.pwd_context.hash(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        await self.db.commit()

        # Send confirmation email
        send_password_changed_email_task.delay(to_email=user.email, first_name=user.first_name)
