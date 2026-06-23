from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
 
from app.services import leave_pdf_service
from app.core.dependencies import get_current_user
from app.db.database import get_db


router = APIRouter()
@router.get(
    "/{leave_id}/approval-letter",
    summary="Download the approval letter PDF for an approved leave request",
)
def download_approval_letter(
    leave_id:int,
    db:Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    pdf_buffer, filename = leave_pdf_service.get_approval_letter(
        db, leave_id, int(current_user.get("sub")), current_user.get("role")
    )
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )