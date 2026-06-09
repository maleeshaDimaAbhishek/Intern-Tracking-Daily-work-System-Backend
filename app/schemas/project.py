
from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional
from pydantic import EmailStr
PROJECT_STATUSES = ["Not Started",
    "Planning",
    "In Progress",
    "On Hold",
    "Testing",
    "Completed",
    "Closed",]

class ProjectCreate(BaseModel):
    name: str
    description: str
    tech_stack: Optional[str]=None
    status:      Optional[str] = "Not Started"
    supervisor_id:Optional[int] = None
class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    tech_stack: Optional[str] = None
    status: str
    supervisor_id: Optional[int] = None
    supervisor_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AssignedUserResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str

    class Config:
        from_attributes = True
class ProjectStatusUpdate(BaseModel):
    status: str
