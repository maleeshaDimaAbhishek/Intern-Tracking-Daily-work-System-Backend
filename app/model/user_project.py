
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy import UniqueConstraint
from app.db.database import Base
from sqlalchemy.orm import relationship
class  UserProject(Base):
    __tablename__="user_projects"
    __table_args__=(
        UniqueConstraint("user_id","project_id",name="uix_user_project"),
    )

    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    project_id=Column(Integer,ForeignKey("projects.id"),nullable=False)
    assigned_at=Column(DateTime,nullable=False)

    user=relationship("User",back_populates="user_projects")
    project=relationship("Project",back_populates="user_projects")