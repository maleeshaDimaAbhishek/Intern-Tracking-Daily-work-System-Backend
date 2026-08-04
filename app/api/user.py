

from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_admin, get_current_admin_or_supervisor, get_current_user
from app.core.security import hash_password
from app.db.database import SessionLocal
from app.services import user_service,project_service
from app.schemas.user import UserCreate, UserResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.repository import project_repo
from app.repository import user_repo 
from pydantic import BaseModel

class ChangePasswordRequest(BaseModel):
    new_password: str

router=APIRouter()

@router.post("/change-password")
def change_password(
    request:ChangePasswordRequest,
    db:Session=Depends(get_db),
    user=Depends(get_current_user)):
    user_id=int(user.get("sub"))

    if len(request.new_password)<8:
        raise HTTPException(status_code=400,detail="Password must be at least 8 characters long")
    user_repo.update_user(db,user_id,{"password":hash_password(request.new_password)})
    user_repo.mark_first_login_complete(db,user_id)
    return {"message":"Password changed successfully"}
@router.post("/register", response_model=UserResponse)
def register(user:UserCreate,db:Session = Depends(get_db),auth_user=Depends(get_current_admin_or_supervisor)):
    try:
        if not user.password or len(user.password)<8:
            raise HTTPException(status_code=400,detail="Password must be at least 8 characters long")
        return user_service.register_user(db,user,user.project_ids)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))
    
@router.get("/", response_model=list[UserResponse])
def get_users(db:Session=Depends(get_db),users=Depends(get_current_admin_or_supervisor)):
    role=users.get("role")
    user_id=int(users.get("sub"))
    if role =="supervisor":
        return user_service.get_interns_by_supervisor(db, user_id)
    return user_service.get_all_users(db)

# REPLACE the get_supervisors endpoint
@router.get("/supervisors", response_model=list[UserResponse])
def get_supervisors(
    db:   Session = Depends(get_db),
    user  = Depends(get_current_user)):
    return user_service.get_supervisors(db)   # ← service layer only

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id:     int,
    update_data: UserCreate,
    db:          Session = Depends(get_db),
    auth_user    = Depends(get_current_admin_or_supervisor)):
    role          = auth_user.get("role")
    supervisor_id = int(auth_user.get("sub"))

    # Supervisor can only edit their own interns
    if role == "supervisor":
        user_service.is_supervisor_of_intern(db, supervisor_id, user_id)
        # Supervisor cannot change intern's role
        update_data.role = "intern"

    data = update_data.dict(
        exclude_unset=True,
        exclude={"project_ids", "password"}
    )
    updated = user_service.update_user(db, user_id, data, update_data.project_ids)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id:int,
    db:Session=Depends(get_db),
    admin=Depends(get_current_admin_or_supervisor)):
    user=user_service.get_user_by_id(db,user_id)
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    return user
@router.get("/{user_id}/projects")
def get_user_projects(
    user_id:int,
    db:Session=Depends(get_db),
    auth_user=Depends(get_current_admin_or_supervisor)):
    role=auth_user.get("role")
    supervisor_id=auth_user.get("sub")
    if role=="supervisor" :
        user_service.is_supervisor_of_intern(db, supervisor_id, user_id)
    # This endpoint describes the target user's assignments. The requester's
    # role must not change the query: a supervisor editing an intern needs the
    # intern's assigned projects, not projects supervised by that intern.
    return project_service.get_assigned_projects_for_user(db, user_id)
@router.delete("/{user_id}")
def soft_delete_user(
    user_id:int,
    db:Session=Depends(get_db),
    admin=Depends(get_current_admin_or_supervisor)):
    success=user_service.soft_delete_user(db,user_id)
    if not success:
        raise HTTPException(status_code=404,detail="User not found")
    return {"message":"User deactivated successfully"}
@router.get("/{user_id}/my-supervisors")
def get_my_supervisors(
    user_id:int,
    db:Session=Depends(get_db),
    user=Depends(get_current_user)):
    return user_service.get_my_supervisors(db,user_id)   # ← service layer only
