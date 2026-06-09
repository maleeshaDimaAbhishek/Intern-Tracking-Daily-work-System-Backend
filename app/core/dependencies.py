
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.auth import verify_token

security=HTTPBearer()
def get_current_user(credentials:HTTPAuthorizationCredentials=Depends(security)):
    # Normalize token in case clients accidentally send quoted strings.
    token = credentials.credentials.strip().strip('"').strip("'")
    if not token or token.lower() in {"null", "undefined"}:
        raise HTTPException(status_code=401,detail="Invalid token")
    payload, err = verify_token(token)
    if err == "expired":
        raise HTTPException(status_code=401, detail="Session expired")
    if err == "invalid":
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload
def get_current_admin(user=Depends(get_current_user)):
    if user.get("role")!="admin":
        raise HTTPException(status_code=403,detail="Admin privileges required")
    return user
def get_current_user_id(user=Depends(get_current_user)):
    # ✅ Returns just the integer ID
    return int(user.get("sub"))
def get_current_admin_or_supervisor(user=Depends(get_current_user)):
    if user.get("role") not in {"admin", "supervisor"}:
        raise HTTPException(status_code=403, detail="Admin or Supervisor privileges required")
    return user
