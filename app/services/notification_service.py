
from sqlalchemy.orm import Session
from fastapi import HTTPException
 
from app.repository import notification_repo
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    MarkReadRequest,
)
def get_my_notifications(db:Session,user_id:int)->NotificationResponse:
    return NotificationListResponse(
        notifications=notification_repo.get_notifications_by_user(db,user_id),
        unread_count=notification_repo.get_unread_count(db,user_id)
    )

def mark_notifications_as_read(db:Session,user_id:int,body:MarkReadRequest)->dict:
    if not body.notification_ids:
        return{"Updated": notification_repo.mark_all_as_read(db,user_id),"message":"All notifications marked as read"}
    return {"Updated": notification_repo.mark_specific_as_read(db,user_id,body.notification_ids),"message":f"{len(body.notification_ids)} notifications marked as read"}
def create_notification(
        db:Session,
        user_id:int,
        leave_request_id:int|None,
        type:str,
        title:str,
        message:str,
)->None:
    notification_repo.create_notitfication(db,{
        "user_id": user_id,
        "leave_request_id": leave_request_id,
        "type": type,
        "title": title,
        "message": message,
        "is_read": False
    })

    