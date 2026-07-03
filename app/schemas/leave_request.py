from pydantic import BaseModel, field_validator, Field
from typing import Optional
from datetime import date, datetime
from app.model.leave_request import LEAVE_TYPES, LEAVE_STATUSES

class LeaveRequestCreate(BaseModel):
    """
    Employee submits this to create a leave request.
    Date fields are all optional here — validation logic
    checks which ones are required based on leave_type.
    """
    leave_type:        str
    reason:            str             = Field(..., min_length=10, max_length=1000)
    emergency_contact: str             = Field(..., min_length=10, max_length=20)
    supervisor_id:     int             # which supervisor to send request to
 
    # Date fields — only relevant ones will be filled
    start_date: Optional[date] = None  # Sick Leave, Personal Leave
    end_date:   Optional[date] = None  # Sick Leave, Personal Leave
    leave_date: Optional[date] = None  # Emergency Leave, Half Day Leave
    session:    Optional[str]  = None  # Half Day Leave only: "Morning" or "Afternoon"

    @field_validator('leave_type')
    def validate_leave_type(cls, value):
        if value not in LEAVE_TYPES:
            raise ValueError(f"Invalid leave type. Must be one of: {', '.join(LEAVE_TYPES)}")
        return value
    @field_validator('session')
    def validate_session(cls, value):
        if value and value not in ['Morning', 'Afternoon']:
            raise ValueError("Session must be either 'Morning' or 'Afternoon'")
        return value
    @field_validator('end_date')
    def validate_dates(cls, end_date, values):
        start_date = values.data.get('start_date')
        if start_date and end_date and end_date < start_date:
            raise ValueError("End date cannot be before start date")
        return end_date
    class Config:
        json_schema_extra = {
            "example": {
                "leave_type": "Sick Leave",
                "reason": "Feeling unwell with a fever and cough.",
                "emergency_contact": "+1234567890",
                "supervisor_id": 1,
                "start_date": "2024-07-01",
                "end_date": "2024-07-03"
            }
        }
class LeaveRequestCancel(BaseModel):
    """Employee leave request cancellation schema."""
    reason:Optional[str]
class SupervisorBasic(BaseModel):
     """Minimal supervisor info embedded in leave response"""
     id:    int
     name:  str
     email: str
     comments: Optional[str]= None
 
     class Config:
        from_attributes = True          
class LeaveApprovalBasic(BaseModel):
    """Minimal approver info embedded in leave response"""
    id:    int
    decision: str
    comments: Optional[str]= None
    decided_at: datetime
    supervisor: SupervisorBasic

    class Config:
        from_attributes = True
class LeaveRequestResponse(BaseModel):
    """
    Full leave request response — returned for all GET endpoints.
    Includes employee info and approval details.
    """
    id:                int
    leave_type:        str
    status:            str
    reason:            str
    emergency_contact: str
    reference:  str
    comments:  Optional[str] = None
 
    # Date fields — nullable depending on leave type
    start_date: Optional[date] = None
    end_date:   Optional[date] = None
    leave_date: Optional[date] = None
    session:    Optional[str]  = None
 
    # Timestamps
    created_at: datetime
    updated_at: datetime
 
    # Employee info
    user_id:    int
    user_name:  Optional[str] = None
    user_email: Optional[str] = None
    user_phone: Optional[str] = None
 
    # Approval details — empty list if not yet decided
    approvals: list[LeaveApprovalBasic] = []
 
    # Medical certificate status — only present for Sick Leave
    medical_status: Optional[str] = None
 
    class Config:
        from_attributes = True
class LeaveRequestSummary(BaseModel):
    """
    Lighter version for list views — no nested approval details,
    but includes the leave reason for supervisor review.
    """
    id:               int
    leave_type:       str
    status:           str
    reason:           str
    comments:         Optional[str] = None
    reference: str
    created_at:       datetime
 
    start_date: Optional[date] = None
    end_date:   Optional[date] = None
    leave_date: Optional[date] = None
    session:    Optional[str]  = None
 
    user_id:    int
    user_name:  Optional[str] = None
    user_email: Optional[str] = None
 
    # Needed so MyLeaves.jsx can show the upload button for Sick Leave
    medical_status: Optional[str] = None
 
    class Config:
        from_attributes = True


