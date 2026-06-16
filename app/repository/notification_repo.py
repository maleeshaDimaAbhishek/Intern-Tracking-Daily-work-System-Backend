from sqlalchemy.orm import Session
from app.model.notification import Notification

def create_notitfication(db:Session,data:dict)->Notification:
    notification = Notification(**data)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification
def get_notifications_by_user(db:Session,user_id:int)->list[Notification]:
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()
def get_unread_count(db:Session,user_id:int)->int:
    return db.query(Notification).filter(Notification.user_id == user_id,Notification.is_read == False).count()
def get_notification_by_id(db:Session,notification_id:int)->Notification:
    return db.query(Notification).filter(Notification.id == notification_id).first()
def mark_as_read(db:Session,notification_id:int)->Notification:
    notification = get_notification_by_id(db,notification_id)
    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    return notification
def mark_all_as_read(db:Session, user_id:int)->int:
    updated=db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).update({"is_read": True})
    db.commit()
    return updated
def mark_specific_as_read(db:Session,user_id:int,notification_ids:list[int])->int:
    updated=db.query(Notification).filter(Notification.user_id == user_id, Notification.id.in_(notification_ids), Notification.is_read == False).update({"is_read": True}, synchronize_session=False)
    db.commit()
    return updated