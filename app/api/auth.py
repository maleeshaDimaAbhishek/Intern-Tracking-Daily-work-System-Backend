from urllib import request

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest
from app.services import auth_service
from app.db.database import get_db
from app.core.otp_store import generate_otp, save_otp, verify_otp, is_verified, clear_otp
from app.core.email_service import send_otp_email
from app.repository import user_repo
from app.core.security import hash_password
from pydantic import BaseModel, EmailStr


router= APIRouter()
class EmailRequest(BaseModel):
     email:EmailStr
class OTPVerifyRequest(BaseModel):
     email:EmailStr
     otp:str
class ResetPasswordRequest(BaseModel):
     email:EmailStr
     new_password:str
#--Existing login-----     
@router.post("/login")
def login(request:LoginRequest,db:Session=Depends(get_db)):
   try:
         return auth_service.login_user(db,request.email,request.password)
   except Exception as e:
         raise HTTPException(status_code=400,detail=str(e))
#---Sned OPT-----
@router.post("/forgot-password")
def forgot_password(request: EmailRequest, db: Session = Depends(get_db)):
    user = user_repo.get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="No account found with this email address."
        )

    otp = generate_otp()
    save_otp(request.email, otp)

    try:
        send_otp_email(request.email, otp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    return {"message": "OTP sent successfully."}
#verify OTP
@router.post("/verify-otp")
def verify_otp_route(request: OTPVerifyRequest):
      if not verify_otp(request.email, request.otp):
          raise HTTPException(status_code=400, detail="Invalid OTP")
      return {"message": "OTP verified successfully."}
#Reset Password
@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
      if not is_verified(request.email):
            raise HTTPException(status_code=400, detail="OTP verification required")
      
      user = user_repo.get_user_by_email(db, request.email)
      if not user:
            raise HTTPException(status_code=404, detail="User not found")
      
      user_repo.update_user(db, user.id, {
        "password": hash_password(request.new_password)
      })
      clear_otp(request.email)  # clean up after success
      
      return {"message": "Password reset successfully."}