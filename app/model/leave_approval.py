from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base

APPROVAL_DECISIONS = ["Approved", "Rejected"]
class LeaveApproval(Base):
    __tablename__= "leave_approvals"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True) 
    leave_request_id = Column(Integer, ForeignKey("leave_requests.id"), nullable=False)
    supervisor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    decision = Column(String, nullable=False)
    comments = Column(Text, nullable=False)
    decided_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    leave_request = relationship("LeaveRequest", back_populates="approval")
    supervisor = relationship("User", foreign_keys=[supervisor_id])