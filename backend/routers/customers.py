"""
Customer router — CRUD + loyalty + purchase history.
"""
from typing import List
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from database import get_db
import models
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


# ============================================
# 5.19 — LOYALTY POINTS
# ============================================
@router.get("/{customer_id}/loyalty")
def get_loyalty_info(customer_id: int, db: Session = Depends(get_db)):
    """Get customer loyalty points and tier."""
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    points = customer.loyalty_points or 0
    tier = "bronze"
    if points >= 5000:
        tier = "gold"
    elif points >= 2000:
        tier = "silver"

    return {
        "customer_id": customer.id,
        "name": customer.name,
        "loyalty_points": points,
        "tier": tier,
        "redeemable_value": round(points * 0.01, 2),  # 1 point = 0.01 EGP
    }


@router.post("/{customer_id}/loyalty/earn")
def earn_loyalty_points(
    customer_id: int,
    amount: Decimal = Query(..., description="Sale total in EGP"),
    db: Session = Depends(get_db),
):
    """Award loyalty points based on sale amount (1 point per 10 EGP)."""
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    points_earned = int(amount / 10)
    customer.loyalty_points = (customer.loyalty_points or 0) + points_earned
    db.commit()
    db.refresh(customer)
    return {"points_earned": points_earned, "total_points": customer.loyalty_points}


@router.post("/{customer_id}/loyalty/redeem")
def redeem_loyalty_points(
    customer_id: int,
    points: int = Query(..., ge=1, description="Points to redeem"),
    db: Session = Depends(get_db),
):
    """Redeem loyalty points as discount (1 point = 0.01 EGP)."""
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    available = customer.loyalty_points or 0
    if points > available:
        raise HTTPException(status_code=400, detail=f"Insufficient points. Available: {available}")

    customer.loyalty_points = available - points
    discount_value = round(points * 0.01, 2)
    db.commit()
    db.refresh(customer)
    return {
        "points_redeemed": points,
        "discount_value": discount_value,
        "remaining_points": customer.loyalty_points,
    }


# ============================================
# 5.20 — CUSTOMER PURCHASE HISTORY
# ============================================
@router.get("/{customer_id}/history")
def get_customer_history(
    customer_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Full purchase history for a specific customer."""
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    sales = (
        db.query(models.Sale)
        .options(joinedload(models.Sale.items))
        .filter(models.Sale.customer_id == customer_id, models.Sale.is_held == False)
        .order_by(models.Sale.sale_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    total_spent = (
        db.query(func.coalesce(func.sum(models.Sale.total), 0))
        .filter(models.Sale.customer_id == customer_id, models.Sale.is_held == False)
        .scalar()
    )

    return {
        "customer_id": customer.id,
        "customer_name": customer.name,
        "total_purchases": len(sales),
        "total_spent": float(total_spent),
        "loyalty_points": customer.loyalty_points or 0,
        "purchases": [
            {
                "id": s.id,
                "date": str(s.sale_date),
                "total": float(s.total),
                "items_count": len(s.items),
                "payment_method": s.payment_method,
            }
            for s in sales
        ],
    }
