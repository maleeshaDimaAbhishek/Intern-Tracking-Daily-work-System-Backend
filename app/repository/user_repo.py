from datetime import datetime, timezone

from sqlalchemy.orm import Session
from app.model.daily_work import DailyWork
from app.model.project import Project
from app.model.user import User
from app.model.user_project import UserProject

def get_user_by_email(db:Session,email:str):
    return db.query(User).filter(User.email==email, User.is_active==True).first()
def get_all_users(db:Session):
    return db.query(User).filter(User.is_active==True).all()

def create_user(db:Session,user_data):
    db_user=User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
def update_user(db:Session,user_id:int,update_data):
    user=db.query(User).filter(User.id==user_id).first()
    if user:
        for key,value in update_data.items():
            setattr(user,key,value)
        db.commit()
        db.refresh(user)
        return user
    return None
def assign_projects(db:Session,user_id:int,project_ids:list[int]):
    for project_id in project_ids:
        exists=db.query(UserProject).filter(UserProject.user_id==user_id, UserProject.project_id==project_id).first()
        if not exists:
            db.add(UserProject(user_id=user_id,project_id=project_id,assigned_at=datetime.now(timezone.utc)))
    db.commit()
def clear_user_projects(db:Session,user_id:int):
    db.query(UserProject).filter(UserProject.user_id==user_id).delete()
    db.commit()
def get_user(db:Session,user_id:int):
    return db.query(User).filter(User.id==user_id).first()  

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
# ADD at the bottom
def get_supervisors(db: Session):
    return db.query(User).filter(
        User.role      == "supervisor",
        User.is_active == True
    ).all()
def mark_first_login_complete(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_first_login = False
        db.commit()
        db.refresh(user)
    return user
def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False    

def soft_delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
        db.refresh(user)
        return True
    return False
def get_supervisors(db: Session):
    return db.query(User).filter(User.role == "supervisor", User.is_active == True).all()
def get_interns_by_supervisor(db: Session, supervisor_id: int):
    return(db.query(User)
    .join(UserProject, User.id == UserProject.user_id)
    .join(Project, UserProject.project_id == Project.id)
    .filter(Project.supervisor_id == supervisor_id, User.role == "intern", User.is_active == True)
    .distinct().all()  
    )
def is_supervisor_of_intern(db: Session, supervisor_id: int, intern_id: int)-> bool:
    result =(db.query(User)
    .join(UserProject, User.id == UserProject.user_id)
    .join(Project, UserProject.project_id == Project.id)
    .filter(Project.supervisor_id == supervisor_id, User.id == intern_id, User.role == "intern", User.is_active == True)
    .first() 
    )
    return result is not None
    
def get_my_supervisors(db: Session, user_id: int):
    return (
        db.query(User)
        .join(Project, Project.supervisor_id == User.id)
        .join(UserProject, UserProject.project_id == Project.id)
        .filter(UserProject.user_id == user_id)
        .distinct()
        .all()
    )