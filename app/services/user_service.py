from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.core.security import hash_password
from app.repository import user_repo
from app.core.email_service import send_welcome_email

def register_user(db:Session,user,project_ids:list[int]=[]):
    existing_user=user_repo.get_user_by_email(db,user.email)

    if existing_user:
        raise Exception("Email already registered")
    plain_password=user.password
    hashed_pw=hash_password(user.password)
    new_user={
        "name":user.name,
        "email":user.email,
        "password":hashed_pw,
        "role": user.role,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "is_first_login": True,
    }
    created=user_repo.create_user(db,new_user)
    if project_ids:
        user_repo.assign_projects(db,created.id,user.project_ids)
    # Send welcome email
    try:
        send_welcome_email(to_email=user.email, name=user.name, password=plain_password, role=user.role)
    except Exception as e:
        print(f"Error sending welcome email: {e}")
    return created
def get_all_users(db):
    return user_repo.get_all_users(db)
def update_user(db,user_id,update_data,project_ids:list[int]=None):
    if "password" in update_data:
        update_data["password"]=hash_password(update_data["password"])
    updated= user_repo.update_user(db,user_id,update_data)
     # If project_ids provided — clear old ones and reassign
    if project_ids is not None:
        user_repo.clear_user_projects(db,user_id)
        if project_ids:
            user_repo.assign_projects(db,user_id,project_ids)
    return updated
def get_user_by_id(db,user_id):
    return user_repo.get_user_by_id(db,user_id)
def soft_delete_user(db,user_id):
    return user_repo.soft_delete_user(db,user_id)
def get_supervisors(db):
    return user_repo.get_supervisors(db)
def get_interns_by_supervisor(db, supervisor_id):
    return user_repo.get_interns_by_supervisor(db, supervisor_id)
def is_supervisor_of_intern(db, supervisor_id, intern_id):
    return user_repo.is_supervisor_of_intern(db, supervisor_id, intern_id)
def get_my_supervisors(db, user_id):
    return user_repo.get_my_supervisors(db, user_id)