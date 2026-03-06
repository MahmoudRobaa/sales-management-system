"""
Sales router — CRUD operations.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
import crud
import cache
from auth import get_current_user_optional, require_manager, TokenData
from routers.deps import log_activity

router = APIRouter(prefix="/api/sales", tags=["Sales"])


@router.get("", response_model=List[schemas.SaleResponse])
def get_sales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_sales(db, skip=skip, limit=limit)


@router.get("/{sale_id}", response_model=schemas.SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = crud.get_sale(db, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


@router.post("", response_model=schemas.SaleResponse)
def create_sale(
    sale: schemas.SaleCreate,
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

        result = crud.create_sale(db, sale, user_id=user_id)
        cache.invalidate_pattern("dashboard:*")
        cache.invalidate_pattern("analytics:*")
        if current_user:
            log_activity(
                db, current_user, "create", "sale", result.id, f"فاتورة بيع #{result.id}"
            )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{sale_id}", response_model=schemas.SaleResponse)
def update_sale(
    sale_id: int,
    sale: schemas.SaleCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_manager),
):
    """Update/Edit an existing sale (manager only) — adjusts inventory accordingly."""
    try:
        user = (
            db.query(models.User)
            .filter(models.User.username == current_user.username)
            .first()
        )
        user_id = user.id if user else None

        result = crud.update_sale(db, sale_id, sale, user_id=user_id)
        cache.invalidate_pattern("dashboard:*")
        cache.invalidate_pattern("analytics:*")
        log_activity(
            db, current_user, "update", "sale", sale_id, f"تعديل فاتورة بيع #{sale_id}"
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{sale_id}")
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_manager),
):
    """Delete a sale (manager only) — restores inventory."""
    if not crud.delete_sale(db, sale_id):
        raise HTTPException(status_code=404, detail="Sale not found")
    cache.invalidate_pattern("dashboard:*")
    cache.invalidate_pattern("analytics:*")
    log_activity(
        db, current_user, "delete", "sale", sale_id, f"حذف فاتورة بيع #{sale_id}"
    )
    return {"message": "Sale deleted successfully"}
