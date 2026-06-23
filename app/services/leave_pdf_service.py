from sqlalchemy.orm import Session
from fastapi import HTTPException, status
 
from app.repository import leave_request_repo
from app.core.pdf_service import generate_approval_letter_pdf

def get_approval_letter(
        db:Session,
        leave_id:int,
        user_id:int,
        role:str,
):
    """
    Returns a PDF buffer for the approval letter.
    Only the employee who owns the leave (or admin) can download it.
    Only APPROVED leaves have a letter to generate.
    """
    leave = leave_request_repo.get_leave_request_by_id(db, leave_id)
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found",
        )
    if role =="intern" and leave.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to download this letter",
        )
    if role =="supervisor" and leave.user_id != user_id and leave.supervisor_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to download this letter",
        )
    if leave.status != "Approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval letter can only be generated for approved leaves",
        )
    if not leave.approval:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No approval record found for this leave request.",
        )
    pdf_buffer = generate_approval_letter_pdf(leave)
    filename = f"Leave_Approval_{leave.reference}.pdf"
    return pdf_buffer, filename

