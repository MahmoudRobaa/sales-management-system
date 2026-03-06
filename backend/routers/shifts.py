"""
Shift Management router (5.9-5.11)
"""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
import models
import schemas
from auth import get_current_user, require_manager, TokenData
from routers.deps import log_activity

router = APIRouter(prefix="/api/shifts", tags=["Shift Management"])


@router.get("", response_model=List[schemas.ShiftResponse])
def list_shifts(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    query = db.query(models.Shift).order_by(models.Shift.id.desc())
    if status:
        query = query.filter(models.Shift.status == status)
    return query.offset(skip).limit(limit).all()


@router.get("/current", response_model=schemas.ShiftResponse)
def get_current_shift(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Get the currently open shift for this user."""
    user = db.query(models.User).filter(models.User.username == current_user.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shift = (
        db.query(models.Shift)
        .filter(models.Shift.user_id == user.id, models.Shift.status == "open")
        .first()
    )
    if not shift:
        raise HTTPException(status_code=404, detail="No open shift found")
    return shift


@router.post("/open", response_model=schemas.ShiftResponse)
def open_shift(
    data: schemas.ShiftOpen,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Open a new shift with float/opening balance."""
    user = db.query(models.User).filter(models.User.username == current_user.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check no open shift exists for this user
    existing = (
        db.query(models.Shift)
        .filter(models.Shift.user_id == user.id, models.Shift.status == "open")
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="You already have an open shift")

    shift = models.Shift(
        user_id=user.id,
        username=user.username,
        opening_balance=data.opening_balance,
        notes=data.notes,
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)

    log_activity(db, current_user, "open", "shift", shift.id, f"فتح وردية #{shift.id}")
    return shift


@router.post("/close", response_model=schemas.ShiftResponse)
def close_shift(
    data: schemas.ShiftClose,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Close the current shift with reconciliation."""
    user = db.query(models.User).filter(models.User.username == current_user.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shift = (
        db.query(models.Shift)
        .filter(models.Shift.user_id == user.id, models.Shift.status == "open")
        .first()
    )
    if not shift:
        raise HTTPException(status_code=404, detail="No open shift to close")

    # Calculate totals from sales in this shift
    shift_sales = db.query(models.Sale).filter(
        models.Sale.shift_id == shift.id,
        models.Sale.is_held == False,
    ).all()
    total_sales = sum(s.total for s in shift_sales)
    total_paid = sum(s.paid for s in shift_sales)
    sales_count = len(shift_sales)

    # Calculate returns
    shift_returns = (
        db.query(models.SaleReturn)
        .filter(models.SaleReturn.created_at >= shift.start_time)
        .all()
    )
    total_returns = sum(r.total for r in shift_returns)
    returns_count = len(shift_returns)

    # Cash drawer logs
    cash_in = db.query(func.coalesce(func.sum(models.CashDrawerLog.amount), 0)).filter(
        models.CashDrawerLog.shift_id == shift.id,
        models.CashDrawerLog.action == "cash_in",
    ).scalar()
    cash_out = db.query(func.coalesce(func.sum(models.CashDrawerLog.amount), 0)).filter(
        models.CashDrawerLog.shift_id == shift.id,
        models.CashDrawerLog.action == "cash_out",
    ).scalar()

    expected = shift.opening_balance + total_paid - total_returns + Decimal(str(cash_in)) - Decimal(str(cash_out))
    variance = data.closing_balance - expected

    shift.end_time = datetime.utcnow()
    shift.closing_balance = data.closing_balance
    shift.expected_balance = expected
    shift.variance = variance
    shift.total_sales = total_sales
    shift.total_returns = total_returns
    shift.total_cash_in = Decimal(str(cash_in))
    shift.total_cash_out = Decimal(str(cash_out))
    shift.sales_count = sales_count
    shift.returns_count = returns_count
    shift.status = "closed"
    shift.notes = data.notes or shift.notes
    shift.closed_by = user.id

    db.commit()
    db.refresh(shift)

    log_activity(db, current_user, "close", "shift", shift.id, f"إغلاق وردية #{shift.id}")
    return shift


@router.get("/{shift_id}", response_model=schemas.ShiftResponse)
def get_shift(shift_id: int, db: Session = Depends(get_db)):
    shift = db.query(models.Shift).filter(models.Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift


@router.get("/{shift_id}/reconciliation")
def get_reconciliation_report(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """End-of-day cash reconciliation report for a shift."""
    shift = db.query(models.Shift).filter(models.Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    sales = db.query(models.Sale).filter(
        models.Sale.shift_id == shift.id,
        models.Sale.is_held == False,
    ).all()

    by_method = {}
    for s in sales:
        method = s.payment_method or "كاش"
        by_method.setdefault(method, {"count": 0, "total": Decimal("0")})
        by_method[method]["count"] += 1
        by_method[method]["total"] += s.paid

    drawer_logs = (
        db.query(models.CashDrawerLog)
        .filter(models.CashDrawerLog.shift_id == shift.id)
        .order_by(models.CashDrawerLog.created_at)
        .all()
    )

    return {
        "shift_id": shift.id,
        "cashier": shift.username,
        "start_time": shift.start_time,
        "end_time": shift.end_time,
        "opening_balance": float(shift.opening_balance),
        "closing_balance": float(shift.closing_balance) if shift.closing_balance else None,
        "expected_balance": float(shift.expected_balance) if shift.expected_balance else None,
        "variance": float(shift.variance) if shift.variance else None,
        "total_sales": float(shift.total_sales or 0),
        "total_returns": float(shift.total_returns or 0),
        "sales_count": shift.sales_count,
        "returns_count": shift.returns_count,
        "payment_breakdown": {k: {"count": v["count"], "total": float(v["total"])} for k, v in by_method.items()},
        "drawer_logs": [
            {
                "id": l.id,
                "action": l.action,
                "amount": float(l.amount),
                "reason": l.reason,
                "created_at": l.created_at,
            }
            for l in drawer_logs
        ],
    }


# ============================================
# CASH DRAWER LOG (5.11)
# ============================================
@router.post("/drawer-log", response_model=schemas.CashDrawerLogResponse)
def log_drawer_action(
    data: schemas.CashDrawerLogCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Log a cash drawer action (open, cash_in, cash_out)."""
    user = db.query(models.User).filter(models.User.username == current_user.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Find open shift
    shift = (
        db.query(models.Shift)
        .filter(models.Shift.user_id == user.id, models.Shift.status == "open")
        .first()
    )

    log_entry = models.CashDrawerLog(
        shift_id=shift.id if shift else None,
        user_id=user.id,
        action=data.action,
        amount=data.amount,
        reason=data.reason,
        notes=data.notes,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    log_activity(db, current_user, data.action, "cash_drawer", log_entry.id, data.reason or data.action)
    return log_entry


@router.get("/drawer-logs", response_model=List[schemas.CashDrawerLogResponse])
def get_drawer_logs(
    shift_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    query = db.query(models.CashDrawerLog).order_by(models.CashDrawerLog.created_at.desc())
    if shift_id:
        query = query.filter(models.CashDrawerLog.shift_id == shift_id)
    return query.limit(limit).all()
