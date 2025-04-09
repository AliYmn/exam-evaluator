from typing import Tuple, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from libs.models.notifications import Notification
from fit_service.api.v1.notification.notification_schemas import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
)
from libs import ErrorCode, ExceptionBase


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(self, user_id: int, notification_data: NotificationCreate) -> NotificationResponse:
        """Create a new notification for a user"""
        new_notification = Notification(
            user_id=user_id,
            title=notification_data.title,
            message=notification_data.message,
            n_type=notification_data.n_type,
            target_screen=notification_data.target_screen,
        )
        self.db.add(new_notification)
        await self.db.commit()
        await self.db.refresh(new_notification)

        return NotificationResponse.model_validate(new_notification)

    async def get_notification(self, notification_id: int, user_id: int) -> NotificationResponse:
        """Get a specific notification by ID"""
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
                Notification.deleted_date.is_(None),
            )
        )
        notification = result.scalars().first()

        if not notification:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return NotificationResponse.model_validate(notification)

    async def list_notifications(
        self, user_id: int, skip: int = 0, limit: int = 100, unread_only: bool = False
    ) -> Tuple[List[NotificationResponse], int]:
        """List all notifications for a user with pagination"""
        # Base query conditions
        conditions = [
            Notification.user_id == user_id,
            Notification.deleted_date.is_(None),
        ]

        # Add unread filter if requested
        if unread_only:
            conditions.append(Notification.is_read == False)

        # Count total notifications
        count_query = select(func.count()).select_from(Notification).where(*conditions)
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar()

        # Get paginated notifications
        query = (
            select(Notification).where(*conditions).order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        )

        result = await self.db.execute(query)
        notifications = result.scalars().all()

        return [NotificationResponse.model_validate(n) for n in notifications], total_count

    async def update_notification(
        self, notification_id: int, user_id: int, notification_data: NotificationUpdate
    ) -> NotificationResponse:
        """Update a specific notification"""
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
                Notification.deleted_date.is_(None),
            )
        )
        notification = result.scalars().first()

        if not notification:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Update fields if provided
        if notification_data.is_read is not None:
            notification.is_read = notification_data.is_read
        if notification_data.title is not None:
            notification.title = notification_data.title
        if notification_data.message is not None:
            notification.message = notification_data.message
        if notification_data.n_type is not None:
            notification.n_type = notification_data.n_type
        if notification_data.target_screen is not None:
            notification.target_screen = notification_data.target_screen

        await self.db.commit()
        await self.db.refresh(notification)

        return NotificationResponse.model_validate(notification)

    async def delete_notification(self, notification_id: int, user_id: int) -> None:
        """Soft delete a specific notification"""
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
                Notification.deleted_date.is_(None),
            )
        )
        notification = result.scalars().first()

        if not notification:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        # Soft delete by setting deleted_date
        notification.deleted_date = datetime.now()
        await self.db.commit()

    async def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user and return the count of updated notifications"""
        # Find all unread notifications for the user
        result = await self.db.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.is_read == False,
                Notification.deleted_date.is_(None),
            )
        )
        notifications = result.scalars().all()

        # Mark each as read
        count = 0
        for notification in notifications:
            notification.is_read = True
            count += 1

        if count > 0:
            await self.db.commit()

        return count
