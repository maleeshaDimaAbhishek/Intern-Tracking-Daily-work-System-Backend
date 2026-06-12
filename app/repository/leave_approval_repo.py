from sqlalchemy.orm import Session, joinedload
from app.model.leave_approval import LeaveApproval

def create_approval(db:Session, data:dict):
    approval = LeaveApproval(**data)
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval
def get_approval_by_leave_request_id(db:Session, leave_request_id:int)->LeaveApproval|None:
    return db.query(LeaveApproval).options(joinedload(LeaveApproval.supervisor)).filter(LeaveApproval.leave_request_id == leave_request_id).first()

def get_approvals_by_supervisor(db:Session, supervisor_id:int)->list[LeaveApproval]:
    return db.query(LeaveApproval).options(joinedload(LeaveApproval.leave_request)).filter(LeaveApproval.supervisor_id == supervisor_id).all()    