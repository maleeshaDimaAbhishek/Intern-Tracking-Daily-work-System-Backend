from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from datetime import datetime, timezone
from app.db.database import Base
from sqlalchemy.orm import relationship

PROJECT_STATUSES = ["Not Started",
    "Planning",
    "In Progress",
    "On Hold",
    "Testing",
    "Completed",
    "Closed",]
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    tech_stack = Column(String, nullable=True)
    status = Column(String, nullable=False, default="Not Started")
    supervisor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_projects = relationship("UserProject", back_populates="project", cascade="all, delete-orphan")
    users = relationship("User", secondary="user_projects", back_populates="projects", viewonly=True)
    supervisor = relationship("User", foreign_keys=[supervisor_id])

    @property
    def supervisor_name(self):
        return self.supervisor.name if self.supervisor else None
