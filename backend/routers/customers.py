"""
Customer router — CRUD operations.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import schemas
import crud

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.get("", response_model=List[schemas.CustomerResponse])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_customers(db, skip=skip, limit=limit)


# NOTE: generate-code must come BEFORE {customer_id} to avoid route conflict
@router.get("/generate-code", response_model=dict)
def generate_customer_code(db: Session = Depends(get_db)):
    return {"code": crud.generate_customer_code(db)}


@router.get("/{customer_id}", response_model=schemas.CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("", response_model=schemas.CustomerResponse)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    existing = crud.get_customer_by_code(db, customer.code)
    if existing:
        raise HTTPException(status_code=400, detail="Customer code already exists")
    return crud.create_customer(db, customer)


@router.put("/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(
    customer_id: int, customer: schemas.CustomerUpdate, db: Session = Depends(get_db)
):
    updated = crud.update_customer(db, customer_id, customer)
    if not updated:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated


@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    if not crud.delete_customer(db, customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}
