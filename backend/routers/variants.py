"""
Product Variants router (5.12)
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
import crud

router = APIRouter(prefix="/api/products/{product_id}/variants", tags=["Product Variants"])


@router.get("", response_model=List[schemas.VariantResponse])
def list_variants(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return (
        db.query(models.ProductVariant)
        .filter(models.ProductVariant.product_id == product_id)
        .all()
    )


@router.post("", response_model=schemas.VariantResponse)
def create_variant(product_id: int, data: schemas.VariantCreate, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = db.query(models.ProductVariant).filter(models.ProductVariant.sku == data.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")

    variant = models.ProductVariant(product_id=product_id, **data.model_dump())
    db.add(variant)

    # Mark product as having variants
    product.has_variants = True
    db.commit()
    db.refresh(variant)
    return variant


@router.put("/{variant_id}", response_model=schemas.VariantResponse)
def update_variant(
    product_id: int, variant_id: int, data: schemas.VariantUpdate, db: Session = Depends(get_db)
):
    variant = (
        db.query(models.ProductVariant)
        .filter(models.ProductVariant.id == variant_id, models.ProductVariant.product_id == product_id)
        .first()
    )
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(variant, key, value)
    db.commit()
    db.refresh(variant)
    return variant


@router.delete("/{variant_id}")
def delete_variant(product_id: int, variant_id: int, db: Session = Depends(get_db)):
    variant = (
        db.query(models.ProductVariant)
        .filter(models.ProductVariant.id == variant_id, models.ProductVariant.product_id == product_id)
        .first()
    )
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    db.delete(variant)

    # Check if product still has other variants
    remaining = (
        db.query(models.ProductVariant)
        .filter(
            models.ProductVariant.product_id == product_id,
            models.ProductVariant.id != variant_id,
        )
        .count()
    )
    if remaining == 0:
        product = crud.get_product(db, product_id)
        if product:
            product.has_variants = False

    db.commit()
    return {"message": "Variant deleted"}
