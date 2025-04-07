from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    title: str = Field(..., description="Notification title", max_length=150)
    message: str = Field(..., description="Notification message")
    n_type: str = Field("info", description="Notification type (info, warning, error, success)", max_length=50)
    target_screen: Optional[str] = Field(
        None, description="Target screen to navigate to when notification is clicked", max_length=100
    )


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = Field(None, description="Whether the notification has been read")
    title: Optional[str] = Field(None, description="Notification title", max_length=150)
    message: Optional[str] = Field(None, description="Notification message")
    n_type: Optional[str] = Field(None, description="Notification type (info, warning, error, success)", max_length=50)
    target_screen: Optional[str] = Field(
        None, description="Target screen to navigate to when notification is clicked", max_length=100
    )


class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    created_date: datetime
    updated_date: Optional[datetime] = None
    deleted_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    count: int
    total: int
