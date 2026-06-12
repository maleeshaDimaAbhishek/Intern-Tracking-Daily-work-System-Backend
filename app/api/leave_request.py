from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.leave_request import (
    LeaveRequestCreate,
    LeaveRequestCancel,
    LeaveRequestResponse,
    LeaveRequestSummary,
)
from app.services import leave_request_service
from app.core.dependencies import (
    get_current_user,
    get_current_user_id,
)
from app.db.database import get_db
router = APIRouter()

@router.post("/",
              response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED,
              summary="Submit a new leave request")
def submit_leave_request(
    body:LeaveRequestCreate,
    db:Session=Depends(get_db),
    user_id:int=Depends(get_current_user_id),
):
    return leave_request_service.submit_leave_request(db, user_id, body)

@router.get("/",response_model=list[LeaveRequestSummary], summary="List all leave requests")
def list_leave_requests(
    db:Session=Depends(get_db),
    current_user:dict=Depends(get_current_user),
):
    return leave_request_service.list_leave_requests(db, current_user)  

@router.get(
    "/{leave_id}",
    response_model=LeaveRequestResponse,
    summary="Get full details of a leave request",
)
def get_leave_request(
    leave_id:     int,
    db:           Session = Depends(get_db),
    current_user: dict    = Depends(get_current_user),
):
    return leave_request_service.get_leave_request(db, leave_id, current_user)
@router.patch(
    "/{leave_id}/cancel",
    response_model=LeaveRequestResponse,
    summary="Cancel a pending leave request",
)
def cancel_leave_request(
    leave_id: int,
    body:     LeaveRequestCancel,
    db:       Session = Depends(get_db),
    user_id:  int     = Depends(get_current_user_id),
):
    return leave_request_service.cancel_leave_request(db, leave_id, user_id)