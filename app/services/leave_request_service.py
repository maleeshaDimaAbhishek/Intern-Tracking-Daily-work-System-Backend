from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone, timedelta
 
from app.repository import leave_request_repo
from app.schemas.leave_request import LeaveRequestCreate
from app.model.leave_request import LeaveRequest, LEAVE_TYPES
from app.model.user import User

def _build_leave_data(schema:LeaveRequestCreate, user_id:int)->dict:
     """Converts the incoming schema into a dict ready for the DB.Also validates that the correct date fields are provided for the chosen leave type."""
     data={
          "user_id": user_id,
          "supervisor_id":schema.supervisor_id,
          "leave_type": schema.leave_type,
            "reason": schema.reason,
            "emergency_contact": schema.emergency_contact,
            "status": "Pending", # Default status
     }
     #validate date fields per leave type
     if schema.leave_type in("Sick Leave","Personal Leave"):
          if not schema.start_date or not schema.end_date:
               raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{schema.leave_type} requires start_date and end_date.")
          data["start_date"]=schema.start_date
          data["end_date"]=schema.end_date
     elif schema.leave_type=="Emergency Leave":
          if not schema.leave_date:
               raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Emergency Leave requires leave_date.")
          data["leave_date"]=schema.leave_date
     elif schema.leave_type=="Half-Day Leave":
          if not schema.leave_date or not schema.session:
               raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Half-Day Leave requires leave_date and session (AM/PM).")
          data["leave_date"]=schema.leave_date
          data["session"]=schema.session
     return data

def _build_response(leave:LeaveRequest)->dict:
     """
    Builds a flat response dict from a LeaveRequest ORM object.Attaches user info and medical status for the frontend."""
     response={
          "id":leave.id,
          "leave_type":leave.leave_type,
          "status":leave.status,
          "reason":leave.reason,
          "emergency_contact":leave.emergency_contact,
          "reference":leave.reference,
          "start_date":leave.start_date,
          "end_date":leave.end_date,
          "leave_date":leave.leave_date,
          "session":leave.session,
          "created_at":leave.created_at,
          "updated_at":leave.updated_at,
          "user_id":leave.user_id,
          "approvals":leave.approval or [],
          "user_name":leave.user.name if leave.user else None,
          "user_email":leave.user.email if leave.user else None,
          "user_phone":leave.user.phone if leave.user else None,
          "medical_status": (
               leave.medical_certificate.status
               if leave.medical_certificate else None
          ),
     }
     return response
def submit_leave_request(db:Session, user_id:int, schema:LeaveRequestCreate)->dict:
     supervisor= db.query(User).filter(User.id==schema.supervisor_id
                                       ,User.role=="supervisor"
                                       ,User.is_active==True,).first()
     if not supervisor:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supervisor not found or inactive.")
     data=_build_leave_data(schema, user_id)
     leave=leave_request_repo.create_leave_request(db, data)
     # Reload with relationships for response
     leave = leave_request_repo.get_leave_request_by_id(db, leave.id)

     _write_audit_log(db,user_id=user_id,
                      leave_request_id=leave.id,
                      action="leave_submitted",
                      previous_value=None,
                      new_value={"status":"Pending","leave_type": leave.leave_type},)
     _create_notification(db, 
                          user_id=schema.supervisor_id,
                          leave_request_id=leave.id,
                          notif_type="leave_submitted",
                          title="New Leave Request Submitted",
                          message=f"{leave.user.name} has submitted a {leave.leave_type} request.Please review.")
     return _build_response(leave)
def get_leave_request(db:Session,
                      leave_id:int,
                      current_user:dict)->dict:
     leave=leave_request_repo.get_leave_request_by_id(db, leave_id)
     if not leave:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found.")
     role = current_user.get("role")
     user_id = int(current_user.get("sub"))

     # Access control — intern can only see their own requests
     if role == "intern" and leave.user_id != user_id:
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this leave request.")
      # Supervisor can only see requests assigned to them
     if role == "supervisor" and leave.supervisor_id != user_id:
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this leave request.")
     return _build_response(leave)

def list_leave_requests(db:Session,
                        current_user:dict,
                        )->list[dict]:
     role = current_user.get("role")
     user_id = int(current_user.get("sub"))
     if role=="admin":
          leaves=leave_request_repo.get_all_leave_requests(db)
     elif role=="supervisor":
          leaves=leave_request_repo.get_leave_requests_for_supervisor(db, user_id)
     else: #intern
          leaves=leave_request_repo.get_leave_requests_by_user(db, user_id)
     return [_build_response(leave) for leave in leaves]
#cancel leave request
def cancel_leave_request(db:Session,
                         leave_id:int,
                         user_id:int)->dict:
     leave=leave_request_repo.get_leave_request_by_id(db, leave_id)
     if not leave:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found.")
     if leave.user_id != user_id:
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this leave request.")
     if leave.status !="Pending":
          raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot cancel a request that is already {leave.status}")
     old_status=leave.status
     leave=leave_request_repo.update_leave_request(db, leave_id, {"status":"Cancelled"})
     _write_audit_log(db,user_id=user_id,
                      leave_request_id=leave.id,
                      action="leave_cancelled",
                      previous_value={"status":old_status},
                      new_value={"status":"Cancelled"},)
     return _build_response(leave)

def _write_audit_log(db:Session, user_id:int, leave_request_id:int, action:str, previous_value, new_value):
     """Writes an entry to the audit log for tracking changes to leave requests."""
     from app.model.audit_log import AuditLog
     log_entry=AuditLog(
          user_id=user_id,
          leave_request_id=leave_request_id,
          action=action,
          previous_value=previous_value,
          new_value=new_value,
     )
     db.add(log_entry)
     db.commit()
def _create_notification(db:Session, user_id:int, leave_request_id:int, notif_type:str, title:str, message:str):
     """Creates a notification for a user regarding a leave request event."""
     from app.model.notification import Notification
     notification=Notification(
          user_id=user_id,
          leave_request_id=leave_request_id,
          type=notif_type,
          title=title,
          message=message,
          is_read=False,
     )
     db.add(notification)
     db.commit()     
