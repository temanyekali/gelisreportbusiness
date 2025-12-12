from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

# JWT Configuration
# CRITICAL: SECRET_KEY must be set in environment variables for production!
# Generate with: python3 -c "import secrets; print(secrets.token_urlsafe(64))"
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    # Development fallback - NEVER use in production!
    import warnings
    warnings.warn(
        "SECRET_KEY not set in environment! Using insecure default. "
        "This is ONLY acceptable in development. "
        "Set SECRET_KEY environment variable for production!",
        RuntimeWarning
    )
    SECRET_KEY = 'INSECURE-DEVELOPMENT-KEY-DO-NOT-USE-IN-PRODUCTION-' + 'x' * 32

ALGORITHM = os.environ.get('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', 43200))

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token tidak valid atau telah kedaluwarsa',
            headers={'WWW-Authenticate': 'Bearer'},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get('sub')
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Kredensial tidak valid',
        )
    return payload
