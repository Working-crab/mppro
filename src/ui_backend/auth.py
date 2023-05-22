from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from ui_backend.config import JWT_TOKEN, ALGORITHM

from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
class UserIn(BaseModel):
    email: str
    password: str
    

def authenticate_user(db_user, password: str):
    if not db_user:
        return False
    if not pwd_context.verify(password, db_user.password):
        return False
    return db_user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_TOKEN, algorithm=ALGORITHM)
    return encoded_jwt
