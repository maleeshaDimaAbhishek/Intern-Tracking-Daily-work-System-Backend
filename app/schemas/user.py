
from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, StringConstraints


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: Optional[Annotated[str, StringConstraints(min_length=8, max_length=72)]] = None
    is_first_login: bool = False
    role: Optional[str] = "intern"
    project_ids: Optional[list[int]] = []
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    created_at: datetime

 #For converting SQLAlchemy model to Pydantic model
    class Config:
        from_attributes = True    