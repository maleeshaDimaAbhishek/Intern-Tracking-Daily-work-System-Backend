
from app.db.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from datetime import datetime, timezone

class DailyWork(Base):
    __tablename__="daily_work"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    submision_time=Column(DateTime, default=datetime.now(timezone.utc))
    date=Column(Date, default=datetime.now(timezone.utc).date)
    