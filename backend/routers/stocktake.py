"""
Stocktake Module router (5.15)
"""
from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
import crud
from auth import get_current_user, require_manager, TokenData
from routers.deps import log_activity

router = APIRouter(prefix="/api/stocktakes", tags=["Stocktake"])


@router.get("", response_model=List[schemas.StocktakeResponse])
def list_stocktakes(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return (
        db.query(models.Stocktake)
        .order_by(models.Stocktake.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("", response_model=schemas.StocktakeResponse)
def create_stocktake(
    data: schemas.StocktakeCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Create a new stocktake. Automatically loads all products with system quantities."""
    user = db.query(models.User).filter(models.User.username == current_user.username).first()
    count = db.query(models.Stocktake).count()
    reference = f"ST{str(count + 1).zfill(4)}"

    stocktake = models.Stocktake(
        reference=reference,
        notes=data.notes,
        created_by=user.id if user else None,
    )
    db.add(stocktake)
    db.flush()

    # Load all active products
    products = db.query(models.Product).filter(models.Product.is_active == True).all()
    for p in products:
        item = models.StocktakeItem(
            stocktake_id=stocktake.id,
            product_id=p.id,
            system_quantity=p.quantity,
        )
        db.add(item)

    db.commit()
    db.refresh(stocktake)

    log_activity(db, current_user, "create", "stocktake", stocktake.id, f"جرد #{reference}")
    return stocktake


@router.get("/{stocktake_id}", response_model=schemas.StocktakeResponse)
def get_stocktake(stocktake_id: int, db: Session = Depends(get_db)):
    st = db.query(models.Stocktake).filter(models.Stocktake.id == stocktake_id).first()
    if not st:
        raise HTTPException(status_code=404, detail="Stocktake not found")

    # Enrich items with product names
    for item in st.items:
        if item.product:
            item.product_name = item.product.name

    return st


@router.put("/{stocktake_id}/count")
def update_counts(
    stocktake_id: int,
    counts: List[schemas.StocktakeItemCreate],
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Submit physical counts for a stocktake."""
    st = db.query(models.Stocktake).filter(models.Stocktake.id == stocktake_id).first()
    if not st:
        raise HTTPException(status_code=404, detail="Stocktake not found")
    if st.status != "in_progress":
        raise HTTPException(status_code=400, detail="Stocktake is not in progress")

    for count in counts:
        item = (
            db.query(models.StocktakeItem)
            .filter(
                models.StocktakeItem.stocktake_id == stocktake_id,
                models.StocktakeItem.product_id == count.product_id,
            )
            .first()
        )
        if item:
            item.counted_quantity = count.counted_quantity
            item.variance = count.counted_quantity - item.system_quantity

    db.commit()
    return {"message": "Counts updated"}


@router.post("/{stocktake_id}/complete")
def complete_stocktake(
    stocktake_id: int,
    apply_adjustments: bool = True,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_manager),
):
    """Complete a stocktake and optionally apply inventory adjustments."""
    st = db.query(models.Stocktake).filter(models.Stocktake.id == stocktake_id).first()
    if not st:
        raise HTTPException(status_code=404, detail="Stocktake not found")
    if st.status != "in_progress":
        raise HTTPException(status_code=400, detail="Stocktake is not in progress")

    adjustments_made = 0
    if apply_adjustments:
        for item in st.items:
            if item.counted_quantity is not None and item.variance != 0:
                product = crud.get_product(db, item.product_id)
                if product:
                    qty_before = product.quantity
                    product.quantity = item.counted_quantity
                    movement = models.InventoryMovement(
                        product_id=product.id,
                        movement_type='stocktake',
                        quantity_before=qty_before,
                        quantity_change=item.counted_quantity - qty_before,
                        quantity_after=item.counted_quantity,
                        reason='stocktake_adjustment',
                        reference_type='stocktake',
                        reference_id=st.id,
                    )
                    db.add(movement)
                    adjustments_made += 1

    st.status = "completed"
    st.completed_at = datetime.utcnow()
    db.commit()

    log_activity(db, current_user, "complete", "stocktake", st.id, f"اكمال جرد #{st.reference}")
    return {"message": "Stocktake completed", "adjustments_made": adjustments_made}
