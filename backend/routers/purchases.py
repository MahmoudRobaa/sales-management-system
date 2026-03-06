"""
Purchase router — CRUD operations.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
import crud
from auth import get_current_user_optional, require_manager, TokenData
from routers.deps import log_activity

router = APIRouter(prefix="/api/purchases", tags=["Purchases"])


@router.get("", response_model=List[schemas.PurchaseResponse])
def get_purchases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_purchases(db, skip=skip, limit=limit)


@router.get("/{purchase_id}", response_model=schemas.PurchaseResponse)
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    purchase = crud.get_purchase(db, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return purchase


@router.post("", response_model=schemas.PurchaseResponse)
def create_purchase(
    purchase: schemas.PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_optional),
):
    try:
        user_id = None
        if current_user:
            user = (
                db.query(models.User)
                .filter(models.User.username == current_user.username)
                .first()
            )
            user_id = user.id if user else None

        result = crud.create_purchase(db, purchase, user_id=user_id)
        if current_user:
            log_activity(
                db, current_user, "create", "purchase", result.id,
                f"فاتورة شراء #{result.id}",
            )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{purchase_id}", response_model=schemas.PurchaseResponse)
def update_purchase(
    purchase_id: int,
    purchase: schemas.PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_manager),
):
    """Update/Edit an existing purchase (manager only) — adjusts inventory accordingly."""
    try:
        user = (
            db.query(models.User)
            .filter(models.User.username == current_user.username)
            .first()
        )
        user_id = user.id if user else None

        result = crud.update_purchase(db, purchase_id, purchase, user_id=user_id)
        log_activity(
            db, current_user, "update", "purchase", purchase_id,
            f"تعديل فاتورة شراء #{purchase_id}",
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{purchase_id}")
def delete_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_manager),
):
    """Delete a purchase (manager only) — reduces inventory."""
    if not crud.delete_purchase(db, purchase_id):
        raise HTTPException(status_code=404, detail="Purchase not found")
    log_activity(
        db, current_user, "delete", "purchase", purchase_id,
        f"حذف فاتورة شراء #{purchase_id}",
    )
    return {"message": "Purchase deleted successfully"}
