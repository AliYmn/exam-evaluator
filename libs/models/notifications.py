from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship

from libs.models.base import BaseModel


# Association table for many-to-many relationship between users and notifications
notification_users = Table(
    "notification_users",
    BaseModel.metadata,
    Column("notification_id", Integer, ForeignKey("notifications.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("is_read", Boolean, default=False),
)


class Notification(BaseModel):
    __tablename__ = "notifications"

    icon = Column(String(50), nullable=True)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(255), nullable=True)
    n_type = Column(String(50), default="info")
    target_screen = Column(String(100), nullable=True)

    users = relationship("User", secondary=notification_users, backref="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, title={self.title})>"
