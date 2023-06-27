import re
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, validator
from datetime import datetime, timedelta
from typing import Optional
from db.queries import db_queries
from ui_backend.config import JWT_TOKEN, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
import asyncio

from common.appLogger import appLogger
logger = appLogger.getLogger(__name__)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

    
class UserIn(BaseModel):
    email: str
    password: str
    
    @validator('email')
    def validate_email(cls, v):
        email_regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.match(email_regex, v):
            raise ValueError('Invalid email address')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(x.isdigit() for x in v):
            raise ValueError('Password must contain at least one digit')
        if not any(x.isupper() for x in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(x.islower() for x in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v
    
    
class TokenData(BaseModel):
    email: Optional[str] = None

    
    
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_TOKEN, algorithms=ALGORITHM)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db_queries.get_user_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    return user


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
