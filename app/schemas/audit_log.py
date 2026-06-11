
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class AuditLogResponse(BaseModel):
     """Single audit log entry"""
     id:int
     user_id: int
     user_name: Optional[str] = None
     leave_request_id: Optional[int] = None
     action: str
     previous_value: Optional[Any] = None
     new_value: Optional[Any] = None
     timestamp: datetime

     class Config:
        from_attributes = True