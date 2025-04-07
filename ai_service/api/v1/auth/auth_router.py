from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ai_service.api.v1.auth.auth_schemas import (
    LoginRequest,
    NewPassword,
    PasswordReset,
    RefreshToken,
    UserCreate,
    UserUpdate,
)
from ai_service.core.services.auth_service import AuthService
from libs.db import get_async_db

# Create router with auth tag
auth_router = APIRouter(tags=["Auth"])

# Set up OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Common dependency for auth service
async def get_ai_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


# User registration endpoint
@auth_router.post("/register", status_code=204)
async def register_user(user_data: UserCreate, ai_service: AuthService = Depends(get_ai_service)):
    await ai_service.create_user(user_data)


# Login endpoint
@auth_router.post("/login")
async def login(login_data: LoginRequest, ai_service: AuthService = Depends(get_ai_service)):
    return await ai_service.authenticate_user(login_data)


# Token refresh endpoint
@auth_router.post("/refresh-token")
async def refresh_access_token(refresh_token: RefreshToken, ai_service: AuthService = Depends(get_ai_service)):
    return await ai_service.refresh_token(refresh_token)


# Current user profile endpoint
@auth_router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme), ai_service: AuthService = Depends(get_ai_service)):
    return await ai_service.get_current_user(token)


# Update user profile endpoint
@auth_router.patch("/me")
async def update_user_profile(
    update_data: UserUpdate, token: str = Depends(oauth2_scheme), ai_service: AuthService = Depends(get_ai_service)
):
    user = await ai_service.get_current_user(token)
    return await ai_service.update_user_profile(user.id, update_data.model_dump(exclude_unset=True))


# Password reset request endpoint
@auth_router.post("/password-reset/request", status_code=204)
async def request_password_reset(email_data: PasswordReset, ai_service: AuthService = Depends(get_ai_service)):
    await ai_service.request_password_reset(email_data)


# Password reset completion endpoint
@auth_router.post("/password-reset/{reset_token}", status_code=204)
async def reset_password(
    reset_token: str, password_data: NewPassword, ai_service: AuthService = Depends(get_ai_service)
):
    await ai_service.reset_password(reset_token, password_data.password)
