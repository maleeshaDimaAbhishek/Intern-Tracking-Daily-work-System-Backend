from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.model.medical_certificate import MEDICAL_STATUSES
 
class MedicalCertificateResponse(BaseModel):
    """
    Returned when checking medical certificate status.
    file_path is null until employee uploads the certificate.
    """
    id:int
    leave_request_id:int
    status: str
    file_path: Optional[str] = None
    submitted_at: Optional[datetime] = None
    deadline:datetime
    reminder_1_sent:Optional[datetime] = None
    reminder_2_sent:Optional[datetime] = None
    created_at: datetime

    days_remaining: Optional[int] = None # How many days remain until deadline (computed in service layer)
    class Config:
        from_attributes = True