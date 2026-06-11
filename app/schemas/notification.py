
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationResponse(BaseModel):
    """Single notification returned to the frontend"""
    id:int
    user_id:int
    leave_request_id: Optional[int] = None
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationListResponse(BaseModel):
    """
    Returned when fetching all notifications for a user.
    Includes unread count for the navbar bell badge.
    """
    notifications: list[NotificationResponse]
    unread_count:  int

class MarkReadRequest(BaseModel):
    notification_ids: list[int]=[]    