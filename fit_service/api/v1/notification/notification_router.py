from fastapi import APIRouter, Depends, Query, status, Header, HTTPException
from typing import Annotated

from fit_service.api.v1.notification.notification_schemas import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
)
from fit_service.core.services.notification_service import NotificationService
from sqlalchemy.ext.asyncio import AsyncSession
from libs.db import get_async_db
from libs.service.auth import AuthService

router = APIRouter(tags=["Notifications"], prefix="/notifications")


def get_notification_service(db: AsyncSession = Depends(get_async_db)) -> NotificationService:
    return NotificationService(db)


def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    authorization: Annotated[str | None, Header()] = None,
    notification_service: NotificationService = Depends(get_notification_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Create a new notification (admin only)"""
    user = await auth_service.get_user_from_token(authorization)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create notifications")
    return await notification_service.create_notification(user.id, notification_data)


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    unread_only: bool = Query(False, description="Filter to show only unread notifications"),
    authorization: Annotated[str | None, Header()] = None,
    notification_service: NotificationService = Depends(get_notification_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """List all notifications for the authenticated user"""
    user = await auth_service.get_user_from_token(authorization)
    notifications, total_count = await notification_service.list_notifications(user.id, skip, limit, unread_only)
    return NotificationListResponse(
        items=notifications,
        count=len(notifications),
        total=total_count,
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    authorization: Annotated[str | None, Header()] = None,
    notification_service: NotificationService = Depends(get_notification_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get a specific notification by ID"""
    user = await auth_service.get_user_from_token(authorization)
    return await notification_service.get_notification(notification_id, user.id)


@router.put("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: int,
    notification_data: NotificationUpdate,
    authorization: Annotated[str | None, Header()] = None,
    notification_service: NotificationService = Depends(get_notification_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update a specific notification"""
    user = await auth_service.get_user_from_token(authorization)
    return await notification_service.update_notification(notification_id, user.id, notification_data)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    authorization: Annotated[str | None, Header()] = None,
    notification_service: NotificationService = Depends(get_notification_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Delete a specific notification"""
    user = await auth_service.get_user_from_token(authorization)
    await notification_service.delete_notification(notification_id, user.id)


@router.post("/mark-all-read", status_code=status.HTTP_200_OK)
async def mark_all_as_read(
    authorization: Annotated[str | None, Header()] = None,
    notification_service: NotificationService = Depends(get_notification_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Mark all notifications as read for the authenticated user"""
    user = await auth_service.get_user_from_token(authorization)
    count = await notification_service.mark_all_as_read(user.id)
    return {"message": f"Marked {count} notifications as read"}
