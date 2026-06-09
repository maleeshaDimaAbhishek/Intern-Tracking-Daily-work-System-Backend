from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.repository import user_repo
from app.core.auth import create_access_token

def login_user(db:Session,email,password):
    user=user_repo.get_user_by_email(db,email)
    if not user:
        raise Exception("User not found")
    if not verify_password(password,user.password):
        raise Exception("Invalid password")
    token=create_access_token({
        "sub":str(user.id),
        "role":user.role,
        "email":user.email,
        })
    return {"access_token":token,"token_type":"bearer","is_first_login": user.is_first_login}