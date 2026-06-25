from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class LeaveVerificationResponse(BaseModel):
    """
    Public-facing verification response.
    Deliberately excludes sensitive fields:
    - No phone number
    - No detailed reason text
    - No emergency contact
    - No internal supervisor comments

    Only confirms the letter is genuine and shows
    the minimum needed to cross-check against the PDF.
    """
    reference: str
    is_valid:         bool          # always True if found — False handled via 404 instead
    employee_name:    str
    leave_type:       str
    status:           str

    start_date: Optional[date] = None
    end_date:   Optional[date] = None
    leave_date: Optional[date] = None
    session:    Optional[str]  = None

    approved_by:   Optional[str]     = None
    approved_date: Optional[datetime] = None

    class Config:
        from_attributes = True