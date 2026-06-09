
from app.model.daily_work import DailyWork
from app.model.user import User
from app.model.project import Project
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone, timedelta
from typing import Any
import logging

logger = logging.getLogger(__name__)

def _today_utc():
    return datetime.now(timezone.utc).date()

def create_task(db: Session, task_data: dict[str, Any]) -> DailyWork:
    try:
        db_task = DailyWork(**task_data)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except SQLAlchemyError as e:
        db.rollback()                        # Rollback on failure
        logger.error("create_task failed: %s", e)
        raise

def get_tasks_by_user(db: Session, user_id: int) -> list[DailyWork]:
    return (
        db.query(DailyWork)
        .filter(DailyWork.user_id == user_id)
        .order_by(DailyWork.date.desc())     # Order add කළා — predictable results
        .all()
    )

def get_last_10_tasks(db: Session, user_id: int) -> list[DailyWork]:
     #Admin version — returns last 10 tasks across ALL projects
    return (
        db.query(DailyWork)
        .filter(DailyWork.user_id == user_id)
        .order_by(DailyWork.date.desc())
        .limit(10)                           # Date filter ඉවත් කළා (redundant)
        .all()
    )
def get_last_10_tasks_by_supervisor(
    db: Session,
    user_id: int,
    supervisor_id: int,
) -> list[DailyWork]:
    """
    Supervisor version — returns last 10 tasks for an intern
    but ONLY for projects that belong to this supervisor.
    """
    return (
        db.query(DailyWork)
        .join(Project, DailyWork.project_id == Project.id)
        .filter(
            DailyWork.user_id == user_id,
            Project.supervisor_id == supervisor_id,   # ← key filter
        )
        .order_by(DailyWork.date.desc())
        .limit(10)
        .all()
    )
def get_yesterday_tasks_all_users(db: Session) -> list[DailyWork]:
    yesterday = _today_utc() - timedelta(days=1)
    return (
        db.query(DailyWork)
        .join(User, DailyWork.user_id == User.id)
        .filter(DailyWork.date == yesterday)
        .order_by(DailyWork.submision_time.desc())  # typo fix: submision→submission
        .all()
    )
def create_task_bulk(db: Session, tasks_data_list: list[dict[str, Any]]) -> list[DailyWork]:
    if not tasks_data_list:                  # Guard: empty list එකක් pass වුනොත්
        return []
    try:
        tasks = [DailyWork(**data) for data in tasks_data_list]
        db.add_all(tasks)
        db.flush()                           # PK populate කරනවා (loop refresh නෑ)
        db.commit()
        return tasks
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("create_task_bulk failed: %s", e)
        raise

def get_tasks_by_user_date_range(
    db: Session,
    user_id: int,
    from_date,
    to_date,
) -> list[DailyWork]:
    return (
        db.query(DailyWork)
        .filter(
            DailyWork.user_id == user_id,
            DailyWork.date >= from_date,
            DailyWork.date <= to_date,
        )
        .order_by(DailyWork.date.desc())
        .all()
    )