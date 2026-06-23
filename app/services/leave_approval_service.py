from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone, timedelta
 
from app.repository import leave_request_repo, leave_approval_repo
from app.schemas.leave_approval import LeaveApprovalCreate
from app.model.leave_request import LeaveRequest
from app.model.audit_log import AuditLog
from app.model.notification import Notification
from app.model.medical_certificate import MedicalCertificate

def _write_audit_log(
        db:Session,
        user_id:int,
        leave_request_id:int,
        action:str,
        previous_value:dict | None,
        new_value:dict | None,
):
    """Writes an entry to the audit log for tracking changes to leave requests."""
    log_entry = AuditLog(
        user_id=user_id,
        leave_request_id=leave_request_id,
        action=action,
        previous_value=previous_value,
        new_value=new_value,
    )
    db.add(log_entry)
    db.commit()
def _create_notification(
        db:Session,
        user_id:int,
        leave_request_id:int,
        notif_type:str,
        title:str,
        message:str,
):
    """Creates a notification for a user regarding a leave request event."""
    notification = Notification(
        user_id=user_id,
        leave_request_id=leave_request_id,
        type=notif_type,
        title=title,
        message=message,
        is_read=False,
    )
    db.add(notification)
    db.commit()
def _create_medical_certificate(
        db:Session,
        leave:LeaveRequest
):
     """
    Auto-created when a Sick Leave is approved.
    Deadline = end_date + 14 days.
    """
     deadline=datetime.combine(leave.end_date, datetime.min.time()).astimezone(timezone.utc) + timedelta(days=14)
     cert=MedicalCertificate(
          leave_request_id=leave.id,
          status="Pending",
          deadline=deadline,
     )
     db.add(cert)
     db.commit()
     db.refresh(cert)
     return cert
def _build_response(leave:LeaveRequest)->dict:
    return{
        "id": leave.id,
        "leave_type": leave.leave_type,
        "status": leave.status,
        "reason": leave.reason,
        "emergency_contact": leave.emergency_contact,
        "reference": leave.reference,
        "start_date": leave.start_date,
        "end_date": leave.end_date,
        "leave_date": leave.leave_date,
        "session": leave.session,
        "created_at": leave.created_at,
        "updated_at": leave.updated_at,
        "user_id": leave.user_id,
        "approval":leave.approval or [],
        "user_name": leave.user.name if leave.user else None,
        "user_email": leave.user.email if leave.user else None,
        "user_phone": leave.user.phone if leave.user else None,
        "medical_status": leave.medical_certificate.status if leave.medical_certificate else None,
    }
            
def decide_leave_request(
        db:Session,
        leave_id:int,
        supervisor_id:int,
        schema:LeaveApprovalCreate,
)-> dict:
    leave=leave_request_repo.get_leave_request_by_id(db, leave_id)
    if not leave:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found.")
    if leave.supervisor_id != supervisor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the assigned supervisor for this leave request.")
    if leave.status != "Pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending leave requests can be approved or rejected.")
    existing=leave_approval_repo.get_approval_by_leave_request_id(db, leave_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This leave request has already been decided.")
    # Create approval record
    old_status=leave.status
    leave_approval_repo.create_approval(db, {
        "leave_request_id": leave_id,
        "supervisor_id":    supervisor_id,
        "decision":         schema.decision,
        "comments":          schema.comments,
    })

    new_status=schema.decision
    leave_request_repo.update_leave_request(
        db,
        leave_id,
        {"status": new_status}
    )
    if schema.decision == "Approved" and leave.leave_type == "Sick Leave":
        _create_medical_certificate(db, leave)
    _write_audit_log(
        db,
        user_id          = supervisor_id,
        leave_request_id = leave_id,
        action           = "leave_approved" if schema.decision == "Approved" else "leave_rejected",
        previous_value   = {"status": old_status},
        new_value        = {
            "status":  new_status,
            "comments": schema.comments,
        },
    )
    if schema.decision == "Approved":
        title   = "Leave Request Approved ✅"
        message = (
            f"Your {leave.leave_type} request "
            f"(Ref: {leave.reference}) has been approved"
            + (f" by your supervisor." )
            + (
                " Please submit your medical certificate within 14 days."
                if leave.leave_type == "Sick Leave" else ""
            )
        )
        notif_type = "leave_approved"
    else:
        title   = "Leave Request Rejected ❌"
        message = (
            f"Your {leave.leave_type} request "
            f"(Ref: {leave.reference}) has been rejected."
            + (f" Reason: {schema.comments}" if schema.comments else "")
        )
        notif_type = "leave_rejected"
    _create_notification(db, 
                         user_id=leave.user_id,
                         leave_request_id=leave.id,
                         notif_type=notif_type,
                         title=title,
                         message=message)
    return _build_response(leave)

def get_pending_for_supervisor(
    db:            Session,
    supervisor_id: int,
) -> list[dict]:
    """
    Returns only Pending requests — what supervisor
    needs to act on right now.
    """
    leaves = leave_request_repo.get_leave_requests_for_supervisor(db, supervisor_id)
    pending = [l for l in leaves if l.status == "Pending"]
    return [_build_response(l) for l in pending]    
 
# ──────────────────────────────────────────────────────────────
# NOTE: Add these imports at the TOP of leave_approval_service.py
# and replace the notification section in decide_leave_request
# ──────────────────────────────────────────────────────────────
#
# from app.core.leave_email_service import (
#     send_leave_approved_email,
#     send_leave_rejected_email,
# )
#
# Then after _create_notification() call, add:
#
# try:
#     if schema.decision == "Approved":
#         send_leave_approved_email(
#             employee_email  = leave.user.email,
#             employee_name   = leave.user.name,
#             supervisor_name = leave.supervisor.name,
#             leave           = leave,
#         )
#     else:
#         send_leave_rejected_email(
#             employee_email  = leave.user.email,
#             employee_name   = leave.user.name,
#             supervisor_name = leave.supervisor.name,
#             leave           = leave,
#             comments        = schema.comments,
#         )
# except Exception as e:
#     # Never let email failure break the approval flow
#     print(f"Email send failed: {e}")