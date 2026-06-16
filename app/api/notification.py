from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
 
from app.schemas.notification import (
    NotificationListResponse,
    MarkReadRequest,
)
from app.services import notification_service
from app.core.dependencies import get_current_user_id
from app.db.database import get_db

router=APIRouter()
@router.get("/",response_model=NotificationListResponse,summary="Fetch all notifications for the current user")
def get_my_notifications(
    db:Session=Depends(get_db),
    user_id:int=Depends(get_current_user_id)
)->NotificationListResponse:
    return notification_service.get_my_notifications(db,user_id)

@router.patch("/read",summary="Mark notifications as read. If no IDs provided, marks all as read")
def mark_notifications_as_read(
    body:MarkReadRequest,
    db:Session=Depends(get_db),
    user_id:int=Depends(get_current_user_id)
)->dict:
    return notification_service.mark_notifications_as_read(db,user_id,body)