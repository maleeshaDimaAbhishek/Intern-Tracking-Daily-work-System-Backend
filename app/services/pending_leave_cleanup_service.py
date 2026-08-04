from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.repository import leave_request_repo


LEAVE_TIMEZONE = ZoneInfo("Asia/Colombo")


def delete_expired_pending_leaves(
    db: Session,
    current_date: date | None = None,
) -> dict:
    """Delete pending leave requests after their relevant leave date has passed."""
    effective_date = current_date or datetime.now(LEAVE_TIMEZONE).date()
    expired_leaves = leave_request_repo.get_expired_pending_leave_requests(
        db,
        effective_date,
    )
    references = [leave.reference for leave in expired_leaves]
    deleted = leave_request_repo.delete_leave_requests(db, expired_leaves)

    return {
        "checked_on": effective_date.isoformat(),
        "deleted": deleted,
        "references": references,
    }
