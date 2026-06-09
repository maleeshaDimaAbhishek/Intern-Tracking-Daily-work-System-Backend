

from datetime import timedelta, datetime
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")
SECRET_KEY = os.getenv("SECRET_KEY")  # In production, use a strong secret key and keep it safe!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set. Please set it to a strong random value.")
def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]), None
    except ExpiredSignatureError:
        return None, "expired"
    except JWTError:
        return None, "invalid"
