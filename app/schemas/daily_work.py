
from datetime import datetime, date
from pydantic import BaseModel
from typing import List, Optional


class DailyWorkCreate(BaseModel):
    description: str
    project_ids: List[int]

class DailyWorkResponse(BaseModel):
    id: int
    description: str
    project_id: Optional[int] = None
    user_id: Optional[int] = None      # ← add
    user_name: Optional[str] = None    # ← add
    submision_time: datetime
    date: date
    
    class Config:
        from_attributes = True