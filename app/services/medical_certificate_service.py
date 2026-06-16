import os
import shutil
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.repository import leave_request_repo
from app.model.medical_certificate import MedicalCertificate
from app.model.notification import Notification
from app.model.audit_log import AuditLog

# ── Where uploaded files are stored ───────────────────────────
UPLOAD_DIR = "uploads/medical_certificates"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Allowed file types ─────────────────────────────────────────
ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "application/pdf",
}

MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


# ──────────────────────────────────────────────────────────────
# UPLOAD MEDICAL CERTIFICATE
# ──────────────────────────────────────────────────────────────

async def upload_medical_certificate(
    db:       Session,
    leave_id: int,
    user_id:  int,
    file:     UploadFile,
) -> dict:
    # ── 1. Fetch the leave request ────────────────────────────
    leave = leave_request_repo.get_leave_request_by_id(db, leave_id)

    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found.",
        )

    # ── 2. Only the owner can upload ──────────────────────────
    if leave.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload certificates for your own leave requests.",
        )

    # ── 3. Only Sick Leave needs a medical certificate ─────────
    if leave.leave_type != "Sick Leave":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medical certificates are only required for Sick Leave.",
        )

    # ── 4. Leave must be approved ─────────────────────────────
    if leave.status != "Approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medical certificate can only be uploaded for approved leaves.",
        )

    # ── 5. Get the medical certificate record ─────────────────
    cert = leave_request_repo.get_medical_certificate(db, leave_id)
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical certificate record not found.",
        )

    # ── 6. Already submitted? ─────────────────────────────────
    if cert.status == "Submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medical certificate already submitted.",
        )

    # ── 7. Validate file type ─────────────────────────────────
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid file type. Allowed: JPEG, PNG, PDF.",
        )

    # ── 8. Validate file size ─────────────────────────────────
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB.",
        )

    # ── 9. Save file to disk ──────────────────────────────────
    # Filename: medical_{leave_id}_{timestamp}.{ext}
    ext       = file.filename.rsplit(".", 1)[-1].lower()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    filename  = f"medical_{leave_id}_{timestamp}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    # ── 10. Update certificate record ────────────────────────
    now = datetime.now(timezone.utc)
    cert = leave_request_repo.update_medical_certificate(
        db, leave_id, {
            "status":       "Submitted",
            "file_path":    file_path,
            "submitted_at": now,
        }
    )

    # ── 11. Audit log ────────────────────────────────────────
    _write_audit_log(
        db,
        user_id          = user_id,
        leave_request_id = leave_id,
        action           = "medical_uploaded",
        previous_value   = {"status": "Pending"},
        new_value        = {
            "status":    "Submitted",
            "file_path": file_path,
        },
    )

    # ── 12. Notify supervisor ─────────────────────────────────
    _create_notification(
        db,
        user_id          = leave.supervisor_id,
        leave_request_id = leave_id,
        notif_type       = "medical_submitted",
        title            = "Medical Certificate Submitted",
        message          = (
            f"{leave.user.name} has uploaded their medical certificate "
            f"for leave request {leave.reference_number}."
        ),
    )

    return _build_cert_response(cert)


# ──────────────────────────────────────────────────────────────
# GET MEDICAL CERTIFICATE STATUS
# ──────────────────────────────────────────────────────────────

def get_medical_certificate_status(
    db:       Session,
    leave_id: int,
    user_id:  int,
    role:     str,
) -> dict:
    leave = leave_request_repo.get_leave_request_by_id(db, leave_id)

    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found.")

    # Access control
    if role == "intern" and leave.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    if role == "supervisor" and leave.supervisor_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    cert = leave_request_repo.get_medical_certificate(db, leave_id)
    if not cert:
        raise HTTPException(
            status_code=404,
            detail="No medical certificate record for this leave.",
        )

    return _build_cert_response(cert)


# ──────────────────────────────────────────────────────────────
# DAILY SCHEDULER — check deadlines and send reminders
# Called once per day by the background scheduler
# ──────────────────────────────────────────────────────────────

def run_medical_certificate_checks(db: Session) -> dict:
    """
    Runs daily. Checks all pending medical certificates and:
    - Sends reminder 1 if 7+ days have passed since leave end
    - Sends reminder 2 if 14 days have passed (deadline day)
    - Marks as Overdue if deadline has passed with no submission
    """
    from app.core.leave_email_service import (
        send_medical_reminder_email,
        send_medical_overdue_email,
    )

    now          = datetime.now(timezone.utc)
    pending_certs = leave_request_repo.get_pending_medical_certificates(db)

    results = {
        "checked":  len(pending_certs),
        "reminder1_sent": 0,
        "reminder2_sent": 0,
        "marked_overdue": 0,
    }

    for cert in pending_certs:
        leave    = cert.leave_request
        if not leave:
            continue

        deadline      = cert.deadline
        days_remaining = (deadline - now).days

        # ── OVERDUE — deadline passed ─────────────────────────
        if now > deadline:
            leave_request_repo.update_medical_certificate(
                db, cert.leave_request_id, {"status": "Overdue"}
            )
            _write_audit_log(
                db,
                user_id          = leave.user_id,
                leave_request_id = leave.id,
                action           = "medical_overdue",
                previous_value   = {"status": "Pending"},
                new_value        = {"status": "Overdue"},
            )
            _create_notification(
                db,
                user_id          = leave.user_id,
                leave_request_id = leave.id,
                notif_type       = "medical_overdue",
                title            = "Medical Certificate Overdue ⚠️",
                message          = (
                    f"Your medical certificate for leave "
                    f"{leave.reference_number} is now overdue. "
                    f"Please contact HR immediately."
                ),
            )
            try:
                send_medical_overdue_email(
                    employee_email = leave.user.email,
                    employee_name  = leave.user.name,
                    leave          = {
                        "leave_type":       leave.leave_type,
                        "start_date":       leave.start_date,
                        "end_date":         leave.end_date,
                        "reference_number": leave.reference_number,
                    },
                )
            except Exception as e:
                print(f"Overdue email failed: {e}")

            results["marked_overdue"] += 1
            continue

        # ── REMINDER 2 — 14 days (deadline day) ──────────────
        # Send if within 0-1 days of deadline and not yet sent
        if days_remaining <= 1 and not cert.reminder_2_sent:
            leave_request_repo.update_medical_certificate(
                db, cert.leave_request_id,
                {"reminder_2_sent": now}
            )
            _create_notification(
                db,
                user_id          = leave.user_id,
                leave_request_id = leave.id,
                notif_type       = "medical_reminder_2",
                title            = "⚠️ Final Reminder: Medical Certificate",
                message          = (
                    f"Last chance! Your medical certificate for "
                    f"{leave.reference_number} is due tomorrow."
                ),
            )
            try:
                send_medical_reminder_email(
                    employee_email   = leave.user.email,
                    employee_name    = leave.user.name,
                    leave            = {
                        "leave_type":       leave.leave_type,
                        "start_date":       leave.start_date,
                        "end_date":         leave.end_date,
                        "reference_number": leave.reference_number,
                    },
                    days_remaining   = days_remaining,
                    reminder_number  = 2,
                )
            except Exception as e:
                print(f"Reminder 2 email failed: {e}")

            results["reminder2_sent"] += 1
            continue

        # ── REMINDER 1 — 7 days remaining ─────────────────────
        if days_remaining <= 7 and not cert.reminder_1_sent:
            leave_request_repo.update_medical_certificate(
                db, cert.leave_request_id,
                {"reminder_1_sent": now}
            )
            _create_notification(
                db,
                user_id          = leave.user_id,
                leave_request_id = leave.id,
                notif_type       = "medical_reminder_1",
                title            = "Medical Certificate Reminder",
                message          = (
                    f"Your medical certificate for "
                    f"{leave.reference_number} is due in "
                    f"{days_remaining} day(s)."
                ),
            )
            try:
                send_medical_reminder_email(
                    employee_email   = leave.user.email,
                    employee_name    = leave.user.name,
                    leave            = {
                        "leave_type":       leave.leave_type,
                        "start_date":       leave.start_date,
                        "end_date":         leave.end_date,
                        "reference_number": leave.reference_number,
                    },
                    days_remaining   = days_remaining,
                    reminder_number  = 1,
                )
            except Exception as e:
                print(f"Reminder 1 email failed: {e}")

            results["reminder1_sent"] += 1

    return results


# ──────────────────────────────────────────────────────────────
# INTERNAL HELPERS
# ──────────────────────────────────────────────────────────────

def _build_cert_response(cert: MedicalCertificate) -> dict:
    now           = datetime.now(timezone.utc)
    days_remaining = max(0, (cert.deadline - now).days)

    return {
        "id":               cert.id,
        "leave_request_id": cert.leave_request_id,
        "status":           cert.status,
        "file_path":        cert.file_path,
        "submitted_at":     cert.submitted_at,
        "deadline":         cert.deadline,
        "reminder_1_sent":  cert.reminder_1_sent,
        "reminder_2_sent":  cert.reminder_2_sent,
        "created_at":       cert.created_at,
        "days_remaining":   days_remaining,
    }


def _write_audit_log(
    db, user_id, leave_request_id, action, previous_value, new_value
):
    log = AuditLog(
        user_id          = user_id,
        leave_request_id = leave_request_id,
        action           = action,
        previous_value   = previous_value,
        new_value        = new_value,
    )
    db.add(log)
    db.commit()


def _create_notification(
    db, user_id, leave_request_id, notif_type, title, message
):
    notif = Notification(
        user_id          = user_id,
        leave_request_id = leave_request_id,
        type             = notif_type,
        title            = title,
        message          = message,
        is_read          = False,
    )
    db.add(notif)
    db.commit()