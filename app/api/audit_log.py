from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.audit_log import AuditLogResponse
from app.services import audit_log_service
from app.core.dependencies import get_current_admin
from app.db.database import get_db

router = APIRouter()


# Admin only — full audit trail
@router.get(
    "/",
    response_model=list[AuditLogResponse],
    summary="[Admin] Get all audit logs",
)
def get_all_audit_logs(
    db:    Session = Depends(get_db),
    _:     dict    = Depends(get_current_admin),
):
    return audit_log_service.get_all_logs(db)


# Audit trail for one specific leave request
@router.get(
    "/leave/{leave_id}",
    response_model=list[AuditLogResponse],
    summary="[Admin] Get audit logs for a specific leave request",
)
def get_logs_by_leave(
    leave_id: int,
    db:       Session = Depends(get_db),
    _:        dict    = Depends(get_current_admin),
):
    return audit_log_service.get_logs_by_leave(db, leave_id)


# Audit trail for one specific user
@router.get(
    "/user/{user_id}",
    response_model=list[AuditLogResponse],
    summary="[Admin] Get audit logs for a specific user",
)
def get_logs_by_user(
    user_id: int,
    db:      Session = Depends(get_db),
    _:       dict    = Depends(get_current_admin),
):
    return audit_log_service.get_logs_by_user(db, user_id)