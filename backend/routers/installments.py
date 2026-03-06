"""
Installment / Credit Sales router (5.6)
"""
from typing import List
from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
import crud
from auth import get_current_user, TokenData
from routers.deps import log_activity

router = APIRouter(prefix="/api/installments", tags=["Installments"])


@router.get("", response_model=List[schemas.InstallmentResponse])
def list_installments(
    sale_id: int = None,
    customer_id: int = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(models.Installment).order_by(models.Installment.due_date)
    if sale_id:
        query = query.filter(models.Installment.sale_id == sale_id)
    if customer_id:
        query = query.filter(models.Installment.customer_id == customer_id)
    if status:
        query = query.filter(models.Installment.status == status)
    return query.offset(skip).limit(limit).all()


@router.post("", response_model=List[schemas.InstallmentResponse])
def create_installment_plan(
    data: schemas.InstallmentCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Create an installment plan for a sale."""
    sale = crud.get_sale(db, data.sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    remaining = sale.total - data.first_payment
    if remaining <= 0:
        raise HTTPException(status_code=400, detail="Sale is already fully paid")

    amount_per = (remaining / data.num_installments).quantize(Decimal("0.01"))
    installments = []

    for i in range(1, data.num_installments + 1):
        due = date.today() + timedelta(days=30 * i)
        inst = models.Installment(
            sale_id=sale.id,
            customer_id=sale.customer_id,
            installment_no=i,
            amount=amount_per if i < data.num_installments else remaining - amount_per * (data.num_installments - 1),
            due_date=due,
        )
        db.add(inst)
        installments.append(inst)

    # Update sale status
    if data.first_payment > 0:
        sale.paid = data.first_payment
        sale.remaining = sale.total - data.first_payment
        sale.status = "جزئي"

    db.commit()
    for inst in installments:
        db.refresh(inst)

    log_activity(db, current_user, "create", "installment", sale.id, f"خطة تقسيط لفاتورة #{sale.invoice_no}")
    return installments


@router.put("/{installment_id}/pay", response_model=schemas.InstallmentResponse)
def pay_installment(
    installment_id: int,
    payment: schemas.InstallmentPayment,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Pay an installment."""
    inst = db.query(models.Installment).filter(models.Installment.id == installment_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Installment not found")
    if inst.status == "paid":
        raise HTTPException(status_code=400, detail="Installment already paid")

    inst.paid_amount = payment.amount
    inst.paid_date = date.today()
    inst.status = "paid" if payment.amount >= inst.amount else "partial"
    inst.notes = payment.notes

    # Update sale
    sale = crud.get_sale(db, inst.sale_id)
    if sale:
        sale.paid += payment.amount
        sale.remaining = max(Decimal("0"), sale.total - sale.paid)
        if sale.remaining <= 0:
            sale.status = "مدفوعة"

    # Update customer balance
    if inst.customer_id:
        customer = crud.get_customer(db, inst.customer_id)
        if customer:
            customer.balance = max(Decimal("0"), customer.balance - payment.amount)

    db.commit()
    db.refresh(inst)

    log_activity(db, current_user, "pay", "installment", inst.id, f"دفع قسط #{inst.installment_no}")
    return inst


@router.get("/overdue", response_model=List[schemas.InstallmentResponse])
def get_overdue_installments(db: Session = Depends(get_db)):
    """Get all overdue installments."""
    today = date.today()
    return (
        db.query(models.Installment)
        .filter(
            models.Installment.due_date < today,
            models.Installment.status.in_(["pending", "partial"]),
        )
        .order_by(models.Installment.due_date)
        .all()
    )
