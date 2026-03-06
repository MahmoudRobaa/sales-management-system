"""
Inventory router — movements and adjustments.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import schemas
import crud

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


@router.get("/movements", response_model=List[schemas.InventoryMovementResponse])
def get_inventory_movements(
    product_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud.get_inventory_movements(db, product_id=product_id, skip=skip, limit=limit)


@router.post("/adjust", response_model=schemas.InventoryMovementResponse)
def adjust_inventory(adjustment: schemas.InventoryAdjustment, db: Session = Depends(get_db)):
    try:
        return crud.adjust_inventory(db, adjustment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
