"""
User management router — CRUD for users (admin only).
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
from auth import (
    get_password_hash,
    require_admin,
    UserCreate,
    UserUpdate,
    UserResponse,
    TokenData,
    validate_password_strength,
)
from routers.deps import log_activity, sanitize_string

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("", response_model=List[UserResponse])
def get_users(
    current_user: TokenData = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get all users (admin only)."""
    return db.query(models.User).all()


@router.post("", response_model=UserResponse)
def create_user(
    user: UserCreate,
    current_user: TokenData = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create new user (admin only)."""
    existing = (
        db.query(models.User).filter(models.User.username == user.username).first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="اسم المستخدم موجود بالفعل")

    # Validate password complexity
    is_valid, error_msg = validate_password_strength(user.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    db_user = models.User(
        username=sanitize_string(user.username),
        password_hash=get_password_hash(user.password),
        full_name=sanitize_string(user.full_name),
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    log_activity(db, current_user, "create", "user", db_user.id, db_user.username)
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: TokenData = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update user (admin only)."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    if user_update.full_name is not None:
        db_user.full_name = sanitize_string(user_update.full_name)
    if user_update.role is not None:
        db_user.role = user_update.role
    if user_update.is_active is not None:
        db_user.is_active = user_update.is_active
    if user_update.password is not None:
        is_valid, error_msg = validate_password_strength(user_update.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        db_user.password_hash = get_password_hash(user_update.password)

    db.commit()
    db.refresh(db_user)

    log_activity(db, current_user, "update", "user", db_user.id, db_user.username)
    return db_user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: TokenData = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete user (admin only)."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    if db_user.username == "admin":
        raise HTTPException(status_code=400, detail="لا يمكن حذف حساب المدير الرئيسي")

    username = db_user.username
    db.delete(db_user)
    db.commit()

    log_activity(db, current_user, "delete", "user", user_id, username)
    return {"message": "تم حذف المستخدم بنجاح"}
