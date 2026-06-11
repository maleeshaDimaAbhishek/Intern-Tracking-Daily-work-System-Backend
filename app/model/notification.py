from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base

NOTIFICATION_TYPES = [
    "leave_submitted",
    "leave_approved",
    "leave_rejected",
    "medical_reminder_1",
    "medical_reminder_2",
    "medical_overdue",
    "medical_submitted",
]
class Notification(Base):
    __tablename__="notifications"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    leave_request_id = Column(Integer, ForeignKey("leave_requests.id"), nullable=True)
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime,nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", foreign_keys=[user_id])
    leave_request = relationship("LeaveRequest", back_populates="notifications")