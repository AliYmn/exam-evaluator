"""
API dependencies for content routes
Reusable auth and service injection
"""

from typing import Annotated
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from content_service.core.services.service import ContentService
from libs.db.db import get_async_db
from libs.service.auth import AuthService
from libs import ExceptionBase, ErrorCode
from libs.models.user import User


async def get_content_service(db: AsyncSession = Depends(get_async_db)) -> ContentService:
    """Inject ContentService with database session"""
    return ContentService(db)


async def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    """Inject AuthService with database session"""
    return AuthService(db)


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    Dependency to get current authenticated user from JWT token.

    Raises:
        ExceptionBase: If token is missing or invalid

    Returns:
        Authenticated user object
    """
    if not authorization:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)

    return await auth_service.get_user_from_token(authorization)


async def get_current_user_from_query_token(
    token: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    Dependency for SSE endpoints that use query parameter token.
    EventSource doesn't support custom headers, so token must be in query string.

    Args:
        token: JWT token from query parameter

    Returns:
        Authenticated user object
    """
    if not token:
        raise ExceptionBase(ErrorCode.INVALID_TOKEN)

    # Add "Bearer " prefix if not present
    auth_token = token if token.startswith("Bearer ") else f"Bearer {token}"
    return await auth_service.get_user_from_token(auth_token)
