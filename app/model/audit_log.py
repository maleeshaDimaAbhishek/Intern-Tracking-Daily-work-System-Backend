from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base

AUDIT_ACTIONS = [
    "leave_created",
    "leave_submitted",
    "leave_approved",
    "leave_rejected",
    "leave_cancelled",
    "leave_updated",
    "medical_uploaded",
    "medical_overdue",]
class AuditLog(Base):
    __tablename__="audit_logs"

    id=Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    leave_request_id = Column(Integer, ForeignKey("leave_requests.id"), nullable=True)
    action = Column(String, nullable=False)
    previous_value = Column(JSON, nullable=True)  # Store previous state as JSON
    new_value = Column(JSON, nullable=True)       # Store new state as JSON
    timestamp = Column(DateTime,nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", foreign_keys=[user_id])
    leave_request = relationship("LeaveRequest", back_populates="audit_logs")