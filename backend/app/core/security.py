import bcrypt
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any
from jose import jwt
from app.core.config import settings

def _hash_password_bytes(password: str) -> bytes:
    """
    Converts password string to bytes safely.
    If UTF-8 encoded password exceeds bcrypt's 72-byte limit, pre-hashes using SHA-256
    to produce a fixed 64-character hex string (64 bytes), preserving all characters
    and preventing length truncation vulnerabilities or ValueError exceptions.
    """
    pwd_bytes = password.encode('utf-8')
    if len(pwd_bytes) > 72:
        return hashlib.sha256(pwd_bytes).hexdigest().encode('utf-8')
    return pwd_bytes

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        pwd_bytes = _hash_password_bytes(plain_password)
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    pwd_bytes = _hash_password_bytes(password)
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')
