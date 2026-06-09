from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date

from app.schemas.daily_work import DailyWorkCreate, DailyWorkResponse
from app.services import daily_work_service
from app.core.dependencies import get_current_admin_or_supervisor, get_current_user_id, get_current_admin
from app.db.database import get_db

# ✅ prefix + tags — main.py එකේ include_router() clean වෙනවා
router = APIRouter()


# ── User endpoints ────────────────────────────────────────────────────────────

@router.post(
    "/submit",
    response_model=list[DailyWorkResponse],
    status_code=status.HTTP_201_CREATED,      # ✅ POST → 201 Created
    summary="Submit today's task",
)
def submit_task(
    task: DailyWorkCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return daily_work_service.submit_task(
        db, user_id, task.description, task.project_ids
    )

@router.get(
    "/my_tasks",
    response_model=list[DailyWorkResponse],
    summary="Get current user's all tasks",
)
def get_my_tasks(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return daily_work_service.get_user_tasks(db, user_id)


# ── Admin endpoints ───────────────────────────────────────────────────────────

@router.get(
    "/user/{user_id}/last10days",
    response_model=list[DailyWorkResponse],
    summary="[Admin] Get last 10 tasks for a user",
)
def get_user_last_10_tasks(
    user_id: int,
    db: Session = Depends(get_db),
    current_user= Depends(get_current_admin_or_supervisor),     # ✅ unused var → underscore convention
):
    role=current_user.get("role")
    supervisor_id=int(current_user.get("sub")) if role=="supervisor" else None
    return daily_work_service.get_last_10_user_tasks(db, user_id, supervisor_id)


@router.get(
    "/yesterday/all",
    response_model=list[DailyWorkResponse],   # ✅ response_model add කළා
    summary="[Admin] Get all users' yesterday tasks",
)
def get_yesterday_all(
    db: Session = Depends(get_db),
    _: None = Depends(get_current_admin_or_supervisor),
):
    return daily_work_service.get_yesterday_tasks(db)


@router.get(
    "/user/{user_id}/range",
    response_model=list[DailyWorkResponse],
    summary="[Admin] Get tasks for a user within a date range",
)
def get_tasks_by_range(
    user_id: int,
    from_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    _: None = Depends(get_current_admin_or_supervisor),
):
    # ✅ Date validation — from_date > to_date වෙන්නේ නැහැ
    if from_date > to_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"from_date ({from_date}) must be ≤ to_date ({to_date})",
        )
    return daily_work_service.get_tasks_by_user_date_range(
        db, user_id, from_date, to_date
    )