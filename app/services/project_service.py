from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.repository import project_repo


from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import logging 

def create_project(db, project_data):

    existing = project_repo.get_project_by_name(db, project_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project name already exists",
        )
    try:
        return project_repo.create_project(db, project_data.dict())
    except IntegrityError as e:
        db.rollback()
        logging.error(f"Database Integrity Error: {str(e)}")
    
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create project. Please check if the assigned Supervisor exists or if required fields are missing.",
        )


def get_all_projects(db):
    return project_repo.get_all_projects(db)


def delete_project(db, project_id: int):
    return project_repo.delete_project(db, project_id)


def get_projects_by_user(db, user_id: int, role: str):
    return project_repo.get_projects_by_user_or_supervisor(db, user_id, role)


def update_project(db, project_id: int, project_data):
    existing = project_repo.get_project_by_name(db, project_data.name)
    if existing and existing.id != project_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project name already exists",
        )

    try:
        return project_repo.update_project(db, project_id, project_data.dict())
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project name already exists",
        )
def get_assigned_users(db, project_id: int):
    return project_repo.get_assigned_users(db, project_id)
def update_project_status(db, project_id: int, status: str):
    return project_repo.update_project_status(db, project_id, status)
def get_supervisor_projects(db, supervisor_id: int):
    return project_repo.get_projects_by_supervisor(db, supervisor_id)
