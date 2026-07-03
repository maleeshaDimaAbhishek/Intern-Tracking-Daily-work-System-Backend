from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from app.model.leave_approval import APPROVAL_DECISIONS

class LeaveApprovalCreate(BaseModel):
    """Leave approval creation schema."""
    decision:str
    comments: str

    @field_validator("decision")
    def validate_decision(cls,v):
        if v not in APPROVAL_DECISIONS:
            raise ValueError(f"decision must be one of: {APPROVAL_DECISIONS}")
        return v
    class Config:
        json_schema_extra = {
            "example": {
                "decision": "Approved",
                "comments": "Approved for 3 days due to medical reasons."
            }
        }
    class LeaveApprovalResponse(BaseModel):
        """Full approval response returned after supervisor decides"""
        id:int
        leave_request_id:int
        supervisor_id:int
        supervisor_name:Optional[str] = None
        decision:str
        comments: str
        decision_date: datetime

        class Config:
            from_attributes = True
