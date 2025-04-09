"""
Notification service for tracker service.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from libs.models.user import User
from libs.models.notifications import Notification, notification_users


class NotificationService:
    """Service for creating and managing notifications."""

    def __init__(self, db: Session):
        self.db = db

    def create_notification_for_active_users(
        self,
        title: str,
        message: str,
        icon: Optional[str] = None,
        link: Optional[str] = None,
        n_type: str = "info",
        target_screen: Optional[str] = None,
    ) -> Notification:
        """
        Create a notification and send it to all active users.

        Args:
            title: Notification title
            message: Notification message
            icon: Icon for the notification (optional)
            link: Link to redirect to (optional)
            n_type: Notification type (default: info)
            target_screen: Target screen to navigate to (optional)

        Returns:
            Created notification
        """
        # Create notification
        notification = Notification(
            title=title, message=message, icon=icon, link=link, n_type=n_type, target_screen=target_screen
        )

        self.db.add(notification)
        self.db.flush()

        # Get all active users
        query = select(User).where(User.is_active == True)
        result = self.db.execute(query)
        active_users = result.scalars().all()

        # Associate notification with users
        for user in active_users:
            self.db.execute(
                notification_users.insert().values(notification_id=notification.id, user_id=user.id, is_read=False)
            )

        self.db.commit()
        return notification

    def create_body_tracker_reminder(self) -> Notification:
        """Create a reminder notification for weekly body tracking."""
        return self.create_notification_for_active_users(
            title="Weekly Body Tracking Reminder",
            message="It's time to update your body measurements for this week! Track your progress to stay motivated.",
            icon="scale",
            n_type="reminder",
            target_screen="body_tracker",
        )

    def create_daily_tracker_reminder(self) -> Notification:
        """Create a reminder notification for daily tracking."""
        return self.create_notification_for_active_users(
            title="Daily Activity Tracking Reminder",
            message="Don't forget to log your daily activities and meals to stay on track with your fitness goals!",
            icon="calendar",
            n_type="reminder",
            target_screen="daily_tracker",
        )
