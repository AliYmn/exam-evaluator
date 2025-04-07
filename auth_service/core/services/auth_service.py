import secrets
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.api.v1.schemas import (
    AppToken,
    LoginRequest,
    PasswordReset,
    RefreshToken,
    Token,
    UserCreate,
    UserResponse,
    to_naive_datetime,
)
from auth_service.core.worker.tasks import (
    send_password_changed_email_task,
    send_password_reset_email_task,
    send_welcome_email_task,
)
from libs import ErrorCode, ExceptionBase, settings
from libs.models.apps import App, app_users
from libs.models.user import User
from libs.redis.cache import CacheService


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.REFRESH_TOKEN_EXPIRE_DAYS = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        self.SECRET_KEY = settings.JWT_SECRET_KEY
        self.ALGORITHM = settings.JWT_ALGORITHM
        self.cache = CacheService()

    # ----- Database Query Methods -----

    async def _get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def _get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def _get_user_by_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == int(user_id)))
        return result.scalars().first()

    async def _get_app_by_name(self, app_name: str) -> Optional[App]:
        result = await self.db.execute(select(App).where(App.name == app_name))
        app = result.scalars().first()
        if not app:
            raise ExceptionBase(ErrorCode.APP_NOT_FOUND)
        return app

    async def _get_user_by_app_identity(self, app_id: int, username: str) -> Optional[User]:
        user = await self._get_user_by_username(username)
        if not user:
            return None

        stmt = select(app_users).where(and_(app_users.c.app_id == app_id, app_users.c.user_id == user.id))
        result = await self.db.execute(stmt)
        association = result.first()
        return user if association else None

    # ----- Password Handling Methods -----

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def _hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    # ----- Token Methods -----

    def _create_token(self, subject: str, expires_delta: timedelta, custom_claims: Dict[str, Any] = None) -> str:
        if custom_claims is None:
            custom_claims = {}
        expire = datetime.now(UTC) + expires_delta
        to_encode = {"exp": expire, "sub": subject, **custom_claims}
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def _decode_token(self, token: str) -> Dict[str, Any]:
        try:
            return jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        except JWTError:
            raise ExceptionBase(ErrorCode.INVALID_TOKEN)

    def _create_token_pair(self, user: User, app_name: str = None, username: str = None) -> Tuple[str, str, int]:
        """Create an access and refresh token pair"""
        # Common user claims
        user_claims = {
            "username": user.username,
            "role": user.role,
            "user_id": str(user.id),
            "email": user.email,
        }

        # Add app info if provided
        if app_name and username:
            user_claims["app_name"] = app_name

        # Access token
        access_token_expires = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self._create_token(
            subject=str(user.id),
            expires_delta=access_token_expires,
            custom_claims=user_claims,
        )

        # Refresh token
        refresh_token_expires = timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_claims = {"token_type": "refresh", **user_claims}
        refresh_token = self._create_token(
            subject=str(user.id),
            expires_delta=refresh_token_expires,
            custom_claims=refresh_claims,
        )

        return access_token, refresh_token, self.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    # ----- Validation Methods -----

    async def _validate_availability(self, username: str = None, email: str = None, app_id: int = None) -> None:
        """Validate username and email availability"""
        if username:
            user = await self._get_user_by_username(username)
            if user:
                raise ExceptionBase(ErrorCode.USERNAME_TAKEN)

        if email:
            user = await self._get_user_by_email(email)
            if user:
                raise ExceptionBase(ErrorCode.EMAIL_TAKEN)

        if username and app_id:
            user = await self._get_user_by_app_identity(app_id, username)
            if user:
                raise ExceptionBase(ErrorCode.CONFLICT, "User identity already exists")

    async def _ensure_user_exists(self, user_id: str) -> User:
        user = await self._get_user_by_id(user_id)
        if not user:
            raise ExceptionBase(ErrorCode.USER_NOT_FOUND)
        return user

    async def _validate_credentials(self, user: Optional[User], password: str) -> User:
        if not user or not self._verify_password(password, user.password_hash):
            raise ExceptionBase(ErrorCode.INVALID_CREDENTIALS)
        if not user.is_active:
            raise ExceptionBase(ErrorCode.INACTIVE_USER)
        return user

    # ----- Cache Methods -----

    async def _get_cached_user(self, user_id: str) -> Optional[UserResponse]:
        cache_key = f"user:{user_id}"
        cached_user = await self.cache.get_cache(cache_key)
        if cached_user:
            try:
                return UserResponse.model_validate_json(cached_user)
            except Exception:
                return None
        return None

    async def _cache_user(self, user: UserResponse, expiration: int = 3600) -> None:
        cache_key = f"user:{user.id}"
        user_json = user.model_dump_json()
        await self.cache.set_cache(cache_key, user_json, expiration)

    async def _clear_user_cache(self, user_id: str) -> None:
        cache_key = f"user:{user_id}"
        await self.cache.delete_cache(cache_key)

    # ----- Public API Methods -----

    async def create_user(self, user_data: UserCreate) -> None:
        """Create a global user account and associate it with an app"""
        # Validate username and email availability
        await self._validate_availability(username=user_data.username, email=user_data.email)

        # Get the app
        app = await self._get_app_by_name(user_data.app_name)

        # Validate app identity availability
        await self._validate_availability(username=user_data.username, app_id=app.id)

        # Create user
        user_dict = user_data.model_dump(exclude={"password", "app_name"})
        user_dict["password_hash"] = self._hash_password(user_data.password)
        new_user = User(**user_dict)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        # Associate user with the app
        stmt = app_users.insert().values(app_id=app.id, user_id=new_user.id, username=user_data.username)
        await self.db.execute(stmt)
        await self.db.commit()

        # Send welcome email
        send_welcome_email_task.delay(to_email=new_user.email, username=new_user.username)

    async def authenticate_app_user(self, login_data: LoginRequest):
        """Authenticate user by app-specific identity"""
        # Get app and user
        app = await self._get_app_by_name(login_data.app_name)
        user = await self._get_user_by_app_identity(app.id, login_data.username)
        user = await self._validate_credentials(user, login_data.password)

        # Update last login time
        user.last_login = datetime.now(UTC).replace(tzinfo=None)
        await self.db.commit()

        # Generate tokens
        access_token, refresh_token, expires_in = self._create_token_pair(
            user, login_data.app_name, login_data.username
        )

        # Return app token
        return AppToken(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
            app_name=login_data.app_name,
            username=login_data.username,
        )

    async def refresh_token(self, refresh_token_data: RefreshToken) -> Token:
        """Refresh token for both global and app-specific authentication"""
        # Validate refresh token
        payload = self._decode_token(refresh_token_data.refresh_token)

        # Check token type
        if "token_type" not in payload or payload["token_type"] != "refresh":
            raise ExceptionBase(ErrorCode.INVALID_TOKEN)

        # Get user from token
        user_id = payload.get("sub")
        if not user_id:
            raise ExceptionBase(ErrorCode.INVALID_TOKEN)

        user = await self._ensure_user_exists(user_id)
        if not user.is_active:
            raise ExceptionBase(ErrorCode.INACTIVE_USER)

        # Get app info if present
        app_name = payload.get("app_name")
        username = payload.get("username")

        # Generate new tokens
        access_token, refresh_token, expires_in = self._create_token_pair(user, app_name, username)

        # Return appropriate token type
        if app_name and username:
            return AppToken(
                access_token=access_token,
                token_type="bearer",
                expires_in=expires_in,
                refresh_token=refresh_token,
                app_name=app_name,
                username=username,
            )
        else:
            return Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=expires_in,
                refresh_token=refresh_token,
            )

    async def get_current_user(self, token: str) -> UserResponse:
        """Get user from token (works for both global and app-specific tokens)"""
        payload = self._decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ExceptionBase(ErrorCode.INVALID_TOKEN)

        # Try to get user from cache
        cached_user = await self._get_cached_user(user_id)
        if cached_user:
            return cached_user

        # Get from database if not in cache
        user = await self._ensure_user_exists(user_id)
        if not user.is_active:
            raise ExceptionBase(ErrorCode.INACTIVE_USER)

        # Cache and return
        user_response = UserResponse.model_validate(user)
        await self._cache_user(user_response)
        return user_response

    async def update_user_profile(self, user_id: str, update_data: Dict[str, Any]) -> UserResponse:
        """Update user profile data"""
        # Get user
        user = await self._ensure_user_exists(user_id)

        # Define allowed fields
        allowed_fields = {
            "first_name",
            "last_name",
            "date_of_birth",
            "profile_picture",
            "gender",
            "language",
            "country",
            "city",
            "address",
            "phone_number",
            "timezone",
            "preferences",
        }

        # Update allowed fields
        for key, value in update_data.items():
            if key in allowed_fields and hasattr(user, key):
                setattr(user, key, value)

        # Save changes
        await self.db.commit()
        await self.db.refresh(user)

        # Clear cache and return updated user
        await self._clear_user_cache(user_id)
        return UserResponse.model_validate(user)

    async def request_password_reset(self, email_data: PasswordReset) -> None:
        """Request password reset, send email with reset token"""
        # Get user by email
        user = await self._get_user_by_email(email_data.email)
        if not user:
            return  # Silently return for security

        # Generate 6-digit reset token
        reset_token = "".join(secrets.choice("0123456789") for _ in range(6))
        user.reset_token = reset_token
        user.reset_token_expiry = to_naive_datetime(datetime.now(UTC) + timedelta(hours=24))
        await self.db.commit()

        # Send reset email
        send_password_reset_email_task.delay(to_email=user.email, username=user.username, reset_token=reset_token)

    async def reset_password(self, reset_token: str, new_password: str) -> None:
        """Reset password using token"""
        # Validate reset token
        now = to_naive_datetime(datetime.now(UTC))
        result = await self.db.execute(
            select(User).where(User.reset_token == reset_token, User.reset_token_expiry > now)
        )
        user = result.scalars().first()
        if not user:
            raise ExceptionBase(ErrorCode.INVALID_RESET_TOKEN)

        # Update password
        user.password_hash = self._hash_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        await self.db.commit()

        # Send confirmation email
        send_password_changed_email_task.delay(to_email=user.email, username=user.username)
