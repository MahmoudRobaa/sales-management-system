"""
Batch / Expiry Tracking router (5.14)
"""
from typing import List, Optional
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
import crud

router = APIRouter(prefix="/api/batches", tags=["Batch / Expiry"])


@router.get("", response_model=List[schemas.BatchResponse])
def list_batches(
    product_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(models.ProductBatch)
    if product_id:
        query = query.filter(models.ProductBatch.product_id == product_id)
    return query.order_by(models.ProductBatch.expiry_date).offset(skip).limit(limit).all()


@router.post("", response_model=schemas.BatchResponse)
def create_batch(data: schemas.BatchCreate, db: Session = Depends(get_db)):
    product = crud.get_product(db, data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    batch = models.ProductBatch(**data.model_dump())
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


@router.get("/expiring")
def get_expiring_batches(days: int = 30, db: Session = Depends(get_db)):
    """Get batches expiring within N days."""
    cutoff = date.today() + timedelta(days=days)
    batches = (
        db.query(models.ProductBatch)
        .filter(
            models.ProductBatch.expiry_date != None,
            models.ProductBatch.expiry_date <= cutoff,
            models.ProductBatch.quantity > 0,
        )
        .order_by(models.ProductBatch.expiry_date)
        .all()
    )
    result = []
    for b in batches:
        product = crud.get_product(db, b.product_id)
        days_left = (b.expiry_date - date.today()).days if b.expiry_date else None
        result.append({
            "id": b.id,
            "product_id": b.product_id,
            "product_name": product.name if product else None,
            "batch_no": b.batch_no,
            "quantity": b.quantity,
            "expiry_date": b.expiry_date,
            "days_until_expiry": days_left,
            "status": "expired" if days_left and days_left < 0 else ("critical" if days_left and days_left < 7 else "warning"),
        })
    return result


@router.delete("/{batch_id}")
def delete_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(models.ProductBatch).filter(models.ProductBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    db.delete(batch)
    db.commit()
    return {"message": "Batch deleted"}
