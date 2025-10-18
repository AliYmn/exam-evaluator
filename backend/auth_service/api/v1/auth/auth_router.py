from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.api.v1.auth.auth_schemas import (
    LoginRequest,
    UserCreate,
    UserUpdate,
)
from auth_service.core.services.service import AuthService
from libs.db import get_async_db
from fastapi_limiter.depends import RateLimiter

# Create router with auth tag
auth_router = APIRouter(tags=["Auth"], prefix="/auth")

# Set up OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Common dependency for auth service
async def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


# User registration endpoint - Limit to 5 registrations per IP address in 5 minutes
@auth_router.post("/register", status_code=201, dependencies=[Depends(RateLimiter(times=5, seconds=300))])
async def register_user(user_data: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    user = await auth_service.create_user(user_data)
    return {
        "message": "User registered successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    }


# Login endpoint - Limit to 10 login attempts per IP address in 1 minute
@auth_router.post("/login", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def login(login_data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.authenticate_user_by_email(login_data)


# Current user profile endpoint
@auth_router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.get_current_user(token)


# Update user profile endpoint
@auth_router.patch("/me", status_code=204)
async def update_user_profile(
    update_data: UserUpdate, token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.get_current_user(token)
    await auth_service.update_user_profile(user.id, update_data.model_dump(exclude_unset=True))
