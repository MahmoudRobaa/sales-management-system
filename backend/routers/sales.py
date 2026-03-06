"""
Sales router — CRUD operations + held/parked sales.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

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


# ============================================
# 5.8 — HELD / PARKED SALES
# ============================================
@router.get("/held", response_model=List[schemas.SaleResponse])
def list_held_sales(db: Session = Depends(get_db)):
    """Get all currently held/parked sales."""
    sales = (
        db.query(models.Sale)
        .options(joinedload(models.Sale.items), joinedload(models.Sale.payments))
        .filter(models.Sale.is_held == True)
        .order_by(models.Sale.created_at.desc())
        .all()
    )
    return sales


@router.put("/{sale_id}/resume", response_model=schemas.SaleResponse)
def resume_held_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user_optional),
):
    """Resume a held sale — convert it to a normal completed sale, deducting stock."""
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if not sale.is_held:
        raise HTTPException(status_code=400, detail="Sale is not held")

    # Validate stock
    for item in sale.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product and item.quantity > product.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}: available {product.quantity}, needed {item.quantity}",
            )

    # Deduct stock + record inventory movement
    for item in sale.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            product.quantity -= item.quantity
            movement = models.InventoryMovement(
                product_id=product.id,
                movement_type="sale",
                quantity_change=-item.quantity,
                quantity_after=product.quantity,
                reference_type="sale",
                reference_id=sale.id,
            )
            db.add(movement)

    # Update customer balance if applicable
    if sale.customer_id:
        customer = db.query(models.Customer).filter(models.Customer.id == sale.customer_id).first()
        if customer:
            customer.balance += sale.total

    sale.is_held = False
    sale.held_name = None
    db.commit()
    db.refresh(sale)

    cache.invalidate_pattern("dashboard:*")
    cache.invalidate_pattern("analytics:*")
    if current_user:
        log_activity(db, current_user, "update", "sale", sale.id, f"استئناف فاتورة محتجزة #{sale.id}")
    return sale
