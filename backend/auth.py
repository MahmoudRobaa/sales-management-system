"""
Authentication module with JWT tokens and password hashing
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import re
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os

# Security configuration
_secret = os.getenv("SECRET_KEY", "")
if not _secret or len(_secret) < 32:
    raise RuntimeError(
        "SECRET_KEY environment variable must be set and at least 32 characters. "
        "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
    )
SECRET_KEY = _secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))  # 24 hours default

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


# ============================================
# SCHEMAS
# ============================================
class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: str = "cashier"  # admin, manager, cashier


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# PASSWORD UTILITIES
# ============================================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    password_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password meets complexity requirements.
    Returns (is_valid, error_message)"""
    if len(password) < 8:
        return False, "كلمة المرور يجب أن تكون 8 أحرف على الأقل (Password must be at least 8 characters)"
    if not re.search(r'[A-Z]', password):
        return False, "كلمة المرور يجب أن تحتوي على حرف كبير (Password must contain an uppercase letter)"
    if not re.search(r'[a-z]', password):
        return False, "كلمة المرور يجب أن تحتوي على حرف صغير (Password must contain a lowercase letter)"
    if not re.search(r'[0-9]', password):
        return False, "كلمة المرور يجب أن تحتوي على رقم (Password must contain a digit)"
    return True, ""


def get_password_hash(password: str) -> str:
    """Hash a password"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


# ============================================
# JWT TOKEN UTILITIES
# ============================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            return None
        return TokenData(username=username, role=role)
    except JWTError:
        return None


# ============================================
# DEPENDENCY FOR PROTECTED ROUTES
# ============================================
async def get_current_user_optional(token: str = Depends(oauth2_scheme)):
    """Get current user from token (optional - returns None if no token)"""
    if not token:
        return None
    
    token_data = decode_token(token)
    if token_data is None:
        return None
    
    return token_data


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from token (required)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    token_data = decode_token(token)
    if token_data is None:
        raise credentials_exception
    
    return token_data


def require_role(allowed_roles: list):
    """Dependency factory to require specific roles"""
    async def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker


# Role shortcuts
require_admin = require_role(["admin"])
require_manager = require_role(["admin", "manager"])
require_cashier = require_role(["admin", "manager", "cashier"])
