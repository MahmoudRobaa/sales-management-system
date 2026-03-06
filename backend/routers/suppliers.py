"""
Supplier router — CRUD operations.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import schemas
import crud

router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])


@router.get("", response_model=List[schemas.SupplierResponse])
def get_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_suppliers(db, skip=skip, limit=limit)


# NOTE: generate-code must come BEFORE {supplier_id} to avoid route conflict
@router.get("/generate-code", response_model=dict)
def generate_supplier_code(db: Session = Depends(get_db)):
    return {"code": crud.generate_supplier_code(db)}


@router.get("/{supplier_id}", response_model=schemas.SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = crud.get_supplier(db, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.post("", response_model=schemas.SupplierResponse)
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    existing = crud.get_supplier_by_code(db, supplier.code)
    if existing:
        raise HTTPException(status_code=400, detail="Supplier code already exists")
    return crud.create_supplier(db, supplier)


@router.put("/{supplier_id}", response_model=schemas.SupplierResponse)
def update_supplier(
    supplier_id: int, supplier: schemas.SupplierUpdate, db: Session = Depends(get_db)
):
    updated = crud.update_supplier(db, supplier_id, supplier)
    if not updated:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return updated


@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    if not crud.delete_supplier(db, supplier_id):
        raise HTTPException(status_code=404, detail="Supplier not found")
    return {"message": "Supplier deleted successfully"}
