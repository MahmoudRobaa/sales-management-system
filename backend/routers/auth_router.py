"""
Authentication router — login, logout, current user.
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from database import get_db
import models
from auth import (
    verify_password,
    create_access_token,
    get_current_user,
    Token,
    UserResponse,
    TokenData,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login and get access token (rate limited: 5 attempts/minute)."""
    user = (
        db.query(models.User)
        .filter(models.User.username == form_data.username)
        .first()
    )

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="اسم المستخدم أو كلمة المرور غير صحيحة",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=401, detail="الحساب غير مفعل")

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    # Log login activity
    log = models.ActivityLog(
        user_id=user.id,
        username=user.username,
        action="login",
        entity_type="auth",
    )
    db.add(log)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
        },
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user information."""
    user = (
        db.query(models.User)
        .filter(models.User.username == current_user.username)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/logout")
def logout(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logout (logs the action)."""
    user = (
        db.query(models.User)
        .filter(models.User.username == current_user.username)
        .first()
    )
    if user:
        log = models.ActivityLog(
            user_id=user.id,
            username=user.username,
            action="logout",
            entity_type="auth",
        )
        db.add(log)
        db.commit()
    return {"message": "تم تسجيل الخروج بنجاح"}
