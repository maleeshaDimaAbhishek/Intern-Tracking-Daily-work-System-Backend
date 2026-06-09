
from sqlalchemy import Column, String,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import Integer

from app.db.database import Base


class User(Base):
    __tablename__="users" 

    id = Column(Integer, primary_key=True, index=True)
    name=Column(String,nullable=False)
    phone=Column(String,nullable=False,unique=True)
    email=Column(String,unique=True,index=True,nullable=False)
    password=Column(String,nullable=False)
    is_first_login=Column(Boolean,default=True,nullable=False)
    role=Column(String,nullable=False,default="intern")
    created_at=Column(String,nullable=False)
    is_active=Column(Boolean,default=True,nullable=False)

    user_projects=relationship("UserProject",back_populates="user",cascade="all, delete-orphan")
    projects=relationship("Project",secondary="user_projects",back_populates="users",viewonly=True)

    
