from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.audit_log import AuditLogResponse
from app.services import audit_log_service
from app.core.dependencies import get_current_admin, get_current_admin_or_supervisor
from app.db.database import get_db

router = APIRouter()


# Admin only — full org-wide audit trail
@router.get(
    "/",
    response_model=list[AuditLogResponse],
    summary="[Admin] Get all audit logs",
)
def get_all_audit_logs(
    db: Session = Depends(get_db),
    _:  dict    = Depends(get_current_admin),
):
    return audit_log_service.get_all_logs(db)


# Audit trail for one specific leave request
# Admin: any leave request. Supervisor: only requests they are
# assigned to — enforced inside the service layer, not here,
# since checking ownership requires looking at the leave record itself.
@router.get(
    "/leave/{leave_id}",
    response_model=list[AuditLogResponse],
    summary="[Admin/Supervisor] Get audit logs for a specific leave request",
)
def get_logs_by_leave(
    leave_id:     int,
    db:           Session = Depends(get_db),
    current_user: dict    = Depends(get_current_admin_or_supervisor),
):
    return audit_log_service.get_logs_by_leave(db, leave_id, current_user)


# Audit trail for one specific user — admin only, this is a
# broader cross-request view that doesn't make sense to scope
# to a single supervisor's team boundary.
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