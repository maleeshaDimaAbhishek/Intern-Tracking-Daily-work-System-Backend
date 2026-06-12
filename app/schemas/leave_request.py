from pydantic import BaseModel, field_validator, Field
from typing import Optional
from datetime import date, datetime
from app.model.leave_request import LEAVE_TYPES, LEAVE_STATUSES

class LeaveRequestCreate(BaseModel):
    """Employee leave request creation schema."""
    leave_type:str
    reason:str = Field(..., min_length=10, max_length=1000)
    emergency_contact:str = Field(..., min_length=10, max_length=15)
    supervisor_id: int

    #Date fields — only relevant ones will be filled
    start_date: Optional[date]= None #sick leave, personal leave
    end_date: Optional[date] = None #sick leave, personal leave
    leave_date: Optional[date] = None #emergency leave, half-day leave
    session: Optional[str] = None #half-day leave: Morning or Afternoon

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
        start_date = values.get('start_date')
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
    reason:Optional[str] = Field(None, min_length=10, max_length=700)
class SupervisorBasic(BaseModel):
     """Minimal supervisor info embedded in leave response"""
     id:    int
     name:  str
     email: str
 
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
    id:int
    leave_type:str
    status:str
    reason:str
    emergency_contact:str
    reference_number:str

    #Date fields — only relevant ones will be filled
    start_date: Optional[date]= None #sick leave, personal leave
    end_date: Optional[date] = None #sick leave, personal leave
    leave_date: Optional[date] = None #emergency leave, half-day leave
    session: Optional[str] = None #half-day leave: Morning or Afternoon

    #Timestamps
    created_at: datetime
    updated_at: datetime

    #Employee info
    user_id: int
    user_name: Optional[str] = None
    user_email: Optional[str] = None    
    user_phone: Optional[str] = None
    #Approval info
    approval:list[LeaveApprovalBasic] = []
    #medical certificate status
    medical_status: Optional[str] = None
    class Config:
        from_attributes = True
class LeaveRequestSummary(BaseModel):
    """
    Lighter version for list views — no nested approval details.
    """
    id:int
    leave_type:str
    status:str
    reason:str
    reference_number:str
    created_at: datetime

    #Date fields — only relevant ones will be filled
    start_date: Optional[date]= None #sick leave, personal leave
    end_date: Optional[date] = None #sick leave, personal leave
    leave_date: Optional[date] = None #emergency leave, half-day leave
    session: Optional[str] = None #half-day leave: Morning or Afternoon

    #Employee info
    user_id: int
    user_name: Optional[str] = None
    user_email: Optional[str] = None    

    class Config:
        from_attributes = True


