import uuid
from sqlalchemy import Column, Integer, String, Date,DateTime, ForeignKey,Text
from datetime import datetime, timezone
from app.db.database import Base
from sqlalchemy.orm import relationship

def generate_reference():
    """Generate a unique reference for each leave request 
    Format: LV-2025-A3F9B2"""
    return f"LV-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:6].upper()}"

LEAVE_TYPES=[
    "Sick Leave",
    "Emergency Leave",
    "Personal Leave",
    "Half-Day Leave",
]
LEAVE_STATUSES=[
    "Pending",
    "Approved",
    "Rejected",
    "Cancelled",
]
class LeaveRequest(Base):
    __tablename__="leave_requests"
    id= Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id= Column(Integer, ForeignKey("users.id"), nullable=False)
    supervisor_id= Column(Integer, ForeignKey("users.id"), nullable=True) # Assigned when supervisor approves

    leave_type= Column(String, nullable=False)
    status= Column(String, nullable=False, default="Pending")
    reason= Column(Text, nullable=False)
    emergency_contact= Column(String, nullable=False)

    start_date= Column(Date, nullable=True)
    end_date= Column(Date, nullable=True)
    leave_date=Column(Date, nullable=True)
    session= Column(String, nullable=True)

    reference= Column(String, unique=True, default=generate_reference, nullable=False)

    created_at= Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at= Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", foreign_keys=[user_id])
    supervisor = relationship("User", foreign_keys=[supervisor_id])
    approval=relationship("LeaveApproval", back_populates="leave_request", cascade="all, delete-orphan")
    medical_certificate=relationship("MedicalCertificate", back_populates="leave_request",uselist=False, cascade="all, delete-orphan")
    notifications=relationship("Notification", back_populates="leave_request", cascade="all, delete-orphan")
    audit_logs=relationship("AuditLog", back_populates="leave_request", cascade="all, delete-orphan")