from app.model.project import Project
from app.model.user_project import UserProject
from app.model.user import User
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload


def create_project(db: Session, project_data):
    db_project = Project(**project_data)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_all_projects(db: Session):
    return db.query(Project).options(joinedload(Project.supervisor)).all()


def get_project_by_name(db: Session, name: str):
    return db.query(Project).filter(Project.name == name).first()


def delete_project(db: Session, project_id: int):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        db.delete(project)
        db.commit()
        return True
    return False


def get_project_by_user(db: Session, user_id: int):
    return (
        db.query(Project)
        .options(joinedload(Project.supervisor))
        .join(UserProject, UserProject.project_id == Project.id)
        .filter(UserProject.user_id == user_id)
        .all()
    )


def update_project(db: Session, project_id: int, update_data: dict):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        for key, value in update_data.items():
            setattr(project, key, value)
        db.commit()
        db.refresh(project)
        return project
    return None

def get_assigned_users(db: Session, project_id: int):
    rows = (
        db.query(User)
        .join(UserProject, UserProject.user_id == User.id)
        .filter(UserProject.project_id == project_id, User.is_active == True)
        .all()
    )
    return [
        {
            "id": user.id,
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
        }
        for user in rows
    ]
def update_project_status(db: Session, project_id: int, status: str):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        project.status = status
        db.commit()
        db.refresh(project)
        return project
    return None
def get_projects_by_supervisor(db: Session, supervisor_id: int):
    return (
        db.query(Project)
        .options(joinedload(Project.supervisor))
        .filter(Project.supervisor_id == supervisor_id)
        .all()
    )
def get_projects_by_user_or_supervisor(db: Session, user_id: int, role: str):
    """
    - Interns  : projects they are assigned to (user_projects table)
    - Supervisors: projects they supervise (supervisor_id column)
    """
    if role == "supervisor":
        return (
            db.query(Project)
            .options(joinedload(Project.supervisor))
            .filter(Project.supervisor_id == user_id)
            .all()
        )
    # intern or any other role — check assignments
    return (
        db.query(Project)
        .options(joinedload(Project.supervisor))
        .join(UserProject, UserProject.project_id == Project.id)
        .filter(UserProject.user_id == user_id)
        .all()
    )