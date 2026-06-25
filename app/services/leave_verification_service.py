from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repository import leave_request_repo


def verify_leave_request(db: Session, reference: str) -> dict:
    """
    Public verification lookup. No auth required.

    Only returns data for APPROVED leave requests — a Pending
    or Rejected request has no "approval letter" to verify,
    so we treat those as not-found to avoid confirming/denying
    the existence of unrelated request states to an anonymous caller.
    """
    leave = leave_request_repo.get_leave_request_by_reference(db, reference)

    if not leave or leave.status != "Approved":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No valid approved leave letter found for this reference number.",
        )

    approval = leave.approval[0] if leave.approval else None

    return {
        "reference":         leave.reference,
        "is_valid":          True,
        "employee_name":     leave.user.name,
        "leave_type":        leave.leave_type,
        "status":            leave.status,
        "start_date":        leave.start_date,
        "end_date":          leave.end_date,
        "leave_date":        leave.leave_date,
        "session":           leave.session,
        "approved_by":       approval.supervisor.name if approval else None,
        "approved_date":     approval.decided_at      if approval else None,
    }