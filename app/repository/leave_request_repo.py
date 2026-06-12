from sqlalchemy.orm import Session, joinedload
from app.model.leave_request import LeaveRequest
from app.model.leave_approval import LeaveApproval
from app.model.medical_certificate import MedicalCertificate
from app.model.user import User

def create_leave_request(db:Session, data:dict)->LeaveRequest:
    """Create a new leave request"""
    leave_request = LeaveRequest(**data)
    db.add(leave_request)
    db.commit()
    db.refresh(leave_request)
    return leave_request
def get_leave_request_by_id(db:Session, leave_request_id:int)->LeaveRequest|None:
    return(
        db.query(LeaveRequest)
        .options(
            joinedload(LeaveRequest.user), # Load employee details
            joinedload(LeaveRequest.approval).joinedload(LeaveApproval.supervisor), # Load approval and supervisor details
            joinedload(LeaveRequest.medical_certificate) # Load medical certificate details    
        )
        .filter(LeaveRequest.id==leave_request_id)
        .first()
    )
def get_leave_request_by_reference(db:Session, reference:str)->LeaveRequest|None:
    return(
        db.query(LeaveRequest)
        .filter(LeaveRequest.reference==reference)
        .first()
    )
def get_leave_requests_by_user(db:Session, user_id:int)->list[LeaveRequest]:
    return(
        db.query(LeaveRequest)
        .options(
            joinedload(LeaveRequest.approval).joinedload(LeaveApproval.supervisor), #
            joinedload(LeaveRequest.medical_certificate) # Load medical certificate details
        )
        .filter(LeaveRequest.user_id==user_id)
        .order_by(LeaveRequest.created_at.desc())
        .all()
    )
def get_leave_requests_for_supervisor(db:Session, supervisor_id:int)->list[LeaveRequest]:
    return (
        db.query(LeaveRequest)
        .options(
            joinedload(LeaveRequest.user),
            joinedload(LeaveRequest.approvals)
                .joinedload(LeaveApproval.supervisor),
            joinedload(LeaveRequest.medical_certificate),
        )
        .filter(
            LeaveRequest.supervisor_id == supervisor_id,
        )
        .order_by(LeaveRequest.created_at.desc())
        .all()
    )
def get_all_leave_requests(db:Session)->list[LeaveRequest]:
    return (
        db.query(LeaveRequest)
        .options(
            joinedload(LeaveRequest.user),
            joinedload(LeaveRequest.approval).joinedload(LeaveApproval.supervisor),
            joinedload(LeaveRequest.medical_certificate),
        )
        .order_by(LeaveRequest.created_at.desc())
        .all()
    )
def update_leave_request(
    db: Session, leave_id: int, update_data: dict
) -> LeaveRequest | None:
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        return None
    for key, value in update_data.items():
        setattr(leave, key, value)
    db.commit()
    db.refresh(leave)
    return leave
def create_medical_certificate(db:Session,data:dict)->MedicalCertificate:
    cert= MedicalCertificate(**data)
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert
def get_medical_certificate(db:Session, leave_request_id:int)->MedicalCertificate|None:
    return (
        db.query(MedicalCertificate)
        .filter(MedicalCertificate.leave_request_id == leave_request_id)
        .first()
    )
def update_medical_certificate(db:Session,leave_request_id:int, up)->MedicalCertificate|None:
    cert= db.query(MedicalCertificate).filter(MedicalCertificate.leave_request_id==leave_request_id).first()
    if not cert:
        return None
    for key, value in up.items():
        setattr(cert, key, value)
    db.commit()
    db.refresh(cert)
    return cert
def get_pending_medical_certificates(db:Session)->list[MedicalCertificate]:
    return (
        db.query(MedicalCertificate)
        .filter(MedicalCertificate.status == "Pending")
        .all()
    )