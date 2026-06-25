"""
api_leave_verification.py

PUBLIC endpoint — no authentication required.
This is intentional: the whole point is that someone
WITHOUT a login (HR at another org, an embassy, a bank)
can scan the QR code and verify the letter is real.

Rate limiting should be added here in production to
prevent someone from brute-forcing reference numbers.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.leave_verification import LeaveVerificationResponse
from app.services import leave_verification_service
from app.db.database import get_db

router = APIRouter()


@router.get(
    "/{reference_number}",
    response_model=LeaveVerificationResponse,
    summary="[Public] Verify a leave approval letter by reference number",
)
def verify_leave(
    reference_number: str,
    db: Session = Depends(get_db),
):
    return leave_verification_service.verify_leave_request(db, reference_number)