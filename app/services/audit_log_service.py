from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repository import audit_log_repo
from app.model.audit_log import AuditLog
def _build_response(log:AuditLog)->dict:
    return{
        "id": log.id,
        "user_id": log.user_id,
        "user_name": log.user.name if log.user else None,
        "leave_request_id": log.leave_request_id,
        "action": log.action,
        "previous_value": log.previous_value,
        "new_value": log.new_value,
        "timestamp": log.timestamp,
    }

def get_all_logs(db:Session)-> list[dict]:
    logs = audit_log_repo.get_all_audit_logs(db)
    return [_build_response(log) for log in logs]
def get_logs_by_leave(db:Session, leave_id:int)-> list[dict]:
    logs= audit_log_repo.get_audit_logs_by_leave(db, leave_id)
    if not logs:
        raise HTTPException(status_code=404, detail="No audit logs found for this leave request")
    return [_build_response(log) for log in logs]
def get_logs_by_user(db:Session, user_id:int)-> list[dict]:
    logs= audit_log_repo.get_audit_logs_by_user(db, user_id)
    if not logs:
        raise HTTPException(status_code=404, detail="No audit logs found for this user")
    return [_build_response(log) for log in logs]
