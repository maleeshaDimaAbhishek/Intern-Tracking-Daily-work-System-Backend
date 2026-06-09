import random
import string
from datetime import datetime, timedelta, timezone

otp_store:dict={}
def generate_otp()->str:
    return ''.join(random.choices(string.digits, k=6))
def save_otp(email:str,otp:str):
    otp_store[email]={
        "otp":otp,
        "expires_at": datetime.now(timezone.utc)+timedelta(minutes=10),
        "verified":False
    }
def verify_otp(email:str,otp:str)->bool:
    record=otp_store.get(email)
    if not record:
        return False
    if datetime.now(timezone.utc)>record["expires_at"]:
        del otp_store[email]
        return False
    if record["otp"]!=otp:
        return False 
    otp_store[email]["verified"]=True
    return True
def is_verified(email:str)->bool:
    record=otp_store.get(email)
    return bool(record and record.get("verified"))
def clear_otp(email:str):
    otp_store.pop(email,None)