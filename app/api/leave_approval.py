from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.leave_approval import LeaveApprovalCreate
from app.schemas.leave_request import LeaveRequestResponse, LeaveRequestSummary
from app.services import leave_approval_service
from app.core.dependencies import (
    get_current_admin_or_supervisor,
    get_current_user_id,
)
from app.db.database import get_db

router = APIRouter()


# ==========================================
# 1. STATIC ROUTES FIRST
# ==========================================

# ──────────────────────────────────────────────────────────────
# GET PENDING REQUESTS
# Supervisor sees only what needs their action
# ──────────────────────────────────────────────────────────────
@router.get(
    "/approval/pending",
    response_model=list[LeaveRequestSummary],
    summary="[Supervisor] Get all pending leave requests assigned to you",
)
def get_pending_requests(
    db:           Session = Depends(get_db),
    current_user  = Depends(get_current_admin_or_supervisor),
):
    supervisor_id = int(current_user.get("sub"))
    return leave_approval_service.get_pending_for_supervisor(
        db, supervisor_id
    )


# ==========================================
# 2. DYNAMIC ROUTES LAST
# ==========================================

# ──────────────────────────────────────────────────────────────
# APPROVE OR REJECT
# Only supervisors (and admins) can hit this endpoint
# ──────────────────────────────────────────────────────────────
@router.post(
    "/{leave_id}/decide",
    response_model=LeaveRequestResponse,
    summary="[Supervisor] Approve or reject a leave request",
)
def decide_leave_request(
    leave_id:     int,
    body:         LeaveApprovalCreate,
    db:           Session = Depends(get_db),
    current_user  = Depends(get_current_admin_or_supervisor),
):
    supervisor_id = int(current_user.get("sub"))
    return leave_approval_service.decide_leave_request(
        db, leave_id, supervisor_id, body
    )