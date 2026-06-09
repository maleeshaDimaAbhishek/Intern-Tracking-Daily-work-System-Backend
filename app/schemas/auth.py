from pydantic import BaseModel,EmailStr, constr
class LoginRequest(BaseModel):
    email: EmailStr
    password: str   