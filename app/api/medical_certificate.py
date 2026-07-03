
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
 
from app.schemas.medical_certificate import MedicalCertificateResponse
from app.services import medical_certificate_service
from app.core.dependencies import get_current_user, get_current_user_id
from app.db.database import get_db
 
router = APIRouter()

@router.post(
    "/{leave_id}/medical/",
    response_model=MedicalCertificateResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload Medical Certificate for approved sick leave",
)
async def upload_medical_certificate(
    leave_id:int,
    file: UploadFile = File(..., description="PDF, JPEG, or PNG. Max 5MB."),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return await medical_certificate_service.upload_medical_certificate(db,leave_id, user_id, file)

@router.get(
    "/{leave_id}/medical",
    response_model=MedicalCertificateResponse,
    summary="Get medical certificate status and days remaining"
)
def get_medical_certificate_status(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: dict    = Depends(get_current_user),
):
    return medical_certificate_service.get_medical_certificate_status(db, leave_id, int(current_user["sub"]),current_user.get("role"))