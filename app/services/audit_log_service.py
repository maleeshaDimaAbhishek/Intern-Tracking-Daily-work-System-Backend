from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repository import audit_log_repo, leave_request_repo
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
def get_logs_by_leave(
    db:           Session,
    leave_id:     int,
    current_user: dict,
) -> list[dict]:
    """
    Admin     → can view audit trail for any leave request.
    Supervisor → can ONLY view it for leave requests they are
                 personally the assigned supervisor for — checked
                 here rather than trusting the router, since a
                 supervisor must not see another supervisor's
                 team's audit history just by guessing a leave_id.
    """
    role    = current_user.get("role")
    user_id = int(current_user.get("sub"))
 
    if role == "supervisor":
        leave = leave_request_repo.get_leave_request_by_id(db, leave_id)
        if not leave or leave.supervisor_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You are not the assigned supervisor for this leave request.",
            )
    elif role != "admin":
        # Interns (or any other role) never get audit trail access —
        # this endpoint isn't wired into their UI, but the service
        # layer should not silently trust that and skip the check.
        raise HTTPException(status_code=403, detail="Access denied.")
 
    logs = audit_log_repo.get_audit_logs_by_leave(db, leave_id)
    if not logs:
        raise HTTPException(
            status_code=404,
            detail="No audit logs found for this leave request."
        )
    return [_build_response(l) for l in logs]
def get_logs_by_user(db:Session, user_id:int)-> list[dict]:
    logs= audit_log_repo.get_audit_logs_by_user(db, user_id)
    if not logs:
        raise HTTPException(status_code=404, detail="No audit logs found for this user")
    return [_build_response(log) for log in logs]
