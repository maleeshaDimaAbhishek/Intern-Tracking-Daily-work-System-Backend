from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.project import ProjectCreate, ProjectResponse, AssignedUserResponse, ProjectStatusUpdate
from app.services import project_service
from app.core.dependencies import get_current_admin, get_current_admin_or_supervisor, get_current_user   
from app.db.database import get_db
from app.model.project import PROJECT_STATUSES

router=APIRouter()

@router.post("/", response_model=ProjectResponse)
def create_project(
    project:ProjectCreate,
    db:Session=Depends(get_db),
    admin=Depends(get_current_admin_or_supervisor)):
    return project_service.create_project(db,project)
@router.get("/", response_model=list[ProjectResponse])
def get_all_projects(
    db:   Session = Depends(get_db),
    user  = Depends(get_current_user)):
    role    = user.get("role")
    user_id = int(user.get("sub"))
    # Supervisor sees only their own projects
    if role == "supervisor":
        return project_service.get_supervisor_projects(db, user_id)
    return project_service.get_all_projects(db)
@router.get("/my", response_model=list[ProjectResponse])
def get_my_projects(
    db:Session=Depends(get_db),
    user=Depends(get_current_user)):
    user_id=int(user.get("sub"))
    role=user.get("role")
    return project_service.get_projects_by_user(db,user_id,role)
@router.delete("/{project_id}")
def delete_project(
    project_id:int,
    db:Session=Depends(get_db),
    admin=Depends(get_current_admin_or_supervisor)):
    return project_service.delete_project(db,project_id)
@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id:int,
    project:ProjectCreate,
    db:Session=Depends(get_db),
    admin=Depends(get_current_admin_or_supervisor)):
    return project_service.update_project(db,project_id,project)
@router.get("/{project_id}/users", response_model=list[AssignedUserResponse])
def get_assigned_users(
    project_id:int,
    db:Session=Depends(get_db),
    admin=Depends(get_current_admin_or_supervisor)):
    return project_service.get_assigned_users(db,project_id)
@router.patch("/{project_id}/status", response_model=ProjectResponse)
def update_project_status(
    project_id:int,
    body:ProjectStatusUpdate,
    db:Session=Depends(get_db),
    admin=Depends(get_current_admin_or_supervisor)):
    if body.status not in PROJECT_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {PROJECT_STATUSES}")
    updated_project = project_service.update_project_status(db, project_id, body.status)
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project
