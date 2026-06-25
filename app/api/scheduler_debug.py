"""
api_scheduler_debug.py

Admin-only debug endpoints for testing the medical certificate
reminder scheduler without waiting real days.

⚠️ These endpoints should be removed or protected further
before production deployment — they're for development testing only.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from app.db.database import get_db
from app.core.dependencies import get_current_admin
from app.services import medical_certificate_service
from app.repository import leave_request_repo

router = APIRouter()


@router.post(
    "/run-medical-check",
    summary="[Admin/Debug] Manually trigger the daily medical certificate check",
)
def run_medical_check_now(
    db: Session = Depends(get_db),
    _:  dict    = Depends(get_current_admin),
):
    """
    Runs the exact same function the scheduler calls automatically
    at 8:00 AM daily. Lets you test reminders/overdue logic instantly
    instead of waiting for the real clock.
    """
    results = medical_certificate_service.run_medical_certificate_checks(db)
    return {
        "message": "Medical certificate check completed.",
        **results,
    }


@router.patch(
    "/backdate-deadline/{leave_id}",
    summary="[Admin/Debug] Backdate a medical certificate's deadline for testing",
)
def backdate_deadline(
    leave_id:     int,
    days_from_now: int,   # e.g. -1 means deadline was yesterday (overdue)
    db:           Session = Depends(get_db),
    _:            dict    = Depends(get_current_admin),
):
    """
    Moves a medical certificate's deadline to simulate time passing.
    Example: days_from_now = -1 → deadline was yesterday → next
    scheduler run will mark it Overdue.
    days_from_now = 0 → deadline is right now → triggers reminder 2.
    """
    new_deadline = datetime.now(timezone.utc) + timedelta(days=days_from_now)

    cert = leave_request_repo.update_medical_certificate(
        db, leave_id, {
            "deadline":        new_deadline,
            # Reset reminder flags so the scheduler treats it as fresh
            "reminder_1_sent": None,
            "reminder_2_sent": None,
        }
    )

    if not cert:
        return {"error": "Medical certificate not found for this leave request."}

    return {
        "message":      "Deadline backdated for testing.",
        "leave_id":      leave_id,
        "new_deadline":  new_deadline,
    }