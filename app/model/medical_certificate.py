from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base


# Possible states of a medical certificate submission
MEDICAL_STATUSES = [
    "Pending",    # approved but certificate not uploaded yet
    "Submitted",  # employee uploaded the certificate
    "Overdue",    # 14 days passed, still not uploaded
]


class MedicalCertificate(Base):
    __tablename__ = "medical_certificates"

    id               = Column(Integer, primary_key=True, index=True, autoincrement=True)
    leave_request_id = Column(Integer, ForeignKey("leave_requests.id"), nullable=False, unique=True)
    # unique=True enforces one-to-one with leave_request

    # ── Status tracking ────────────────────────────────────────
    status     = Column(String,   nullable=False, default="Pending")
    file_path  = Column(String,   nullable=True)   # path to uploaded file, null until submitted
    submitted_at = Column(DateTime, nullable=True)  # when employee uploaded it

    # ── Deadline = leave end_date + 14 days (set when created) ─
    deadline   = Column(DateTime, nullable=False)

    # ── Reminder tracking — null until email is sent ───────────
    reminder_1_sent = Column(DateTime, nullable=True)   # sent at 7 days
    reminder_2_sent = Column(DateTime, nullable=True)   # sent at 14 days

    # ── Timestamps ─────────────────────────────────────────────
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # ── Relationships ───────────────────────────────────────────
    leave_request = relationship("LeaveRequest", back_populates="medical_certificate")