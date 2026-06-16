from sqlalchemy.orm import Session, joinedload
from app.model.audit_log import AuditLog
from app.model.user import User
def get_all_audit_logs(db:Session)-> list[AuditLog]:
    return db.query(AuditLog).options(joinedload(AuditLog.user)).order_by(AuditLog.timestamp.desc()).all()

def get_audit_logs_by_leave(
        db: Session, leave_id: int
)-> list[AuditLog]:
    return db.query(AuditLog).options(joinedload(AuditLog.user)).filter(AuditLog.leave_request_id == leave_id).order_by(AuditLog.timestamp.desc()).all()

def get_audit_logs_by_user(
        db: Session, user_id: int
) -> list[AuditLog]:
    return db.query(AuditLog).options(joinedload(AuditLog.user)).filter(AuditLog.user_id == user_id).order_by(AuditLog.timestamp.desc()).all()