"""
Cash management router — deposit, withdraw, balance, transactions.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from auth import get_current_user, TokenData
from routers.deps import log_activity

router = APIRouter(prefix="/api/cash", tags=["Cash Management"])


@router.get("/balance", response_model=schemas.CashBalanceResponse)
def get_cash_balance(db: Session = Depends(get_db)):
    """Get current cash balance from cash_transactions."""
    try:
        result = db.execute(
            text(
                "SELECT balance_after, created_at "
                "FROM cash_transactions ORDER BY created_at DESC LIMIT 1"
            )
        ).fetchone()

        if result:
            return {"balance": float(result[0]), "last_updated": result[1]}
        return {"balance": 0.0, "last_updated": None}
    except Exception:
        return {"balance": 0.0, "last_updated": None}


@router.get("/transactions", response_model=List[schemas.CashTransactionResponse])
def get_cash_transactions(
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    """Get cash transaction history."""
    try:
        result = db.execute(
            text(
                "SELECT ct.id, ct.transaction_type, ct.amount, ct.balance_before, "
                "ct.balance_after, ct.reference_type, ct.reference_id, ct.description, "
                "ct.created_by, u.full_name as created_by_name, ct.created_at "
                "FROM cash_transactions ct "
                "LEFT JOIN users u ON ct.created_by = u.id "
                "ORDER BY ct.created_at DESC LIMIT :limit"
            ),
            {"limit": limit},
        ).fetchall()

        return [
            {
                "id": row[0],
                "transaction_type": row[1],
                "amount": float(row[2]),
                "balance_before": float(row[3]),
                "balance_after": float(row[4]),
                "reference_type": row[5],
                "reference_id": row[6],
                "description": row[7],
                "created_by": row[8],
                "created_by_name": row[9],
                "created_at": row[10],
            }
            for row in result
        ]
    except Exception:
        return []


@router.post("/deposit", response_model=schemas.CashTransactionResponse)
def deposit_cash(
    deposit: schemas.CashDeposit,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deposit cash/capital."""
    try:
        balance_result = db.execute(
            text(
                "SELECT balance_after FROM cash_transactions "
                "ORDER BY created_at DESC LIMIT 1"
            )
        ).fetchone()

        balance_before = float(balance_result[0]) if balance_result else 0.0
        balance_after = balance_before + float(deposit.amount)

        user = (
            db.query(models.User)
            .filter(models.User.username == current_user.username)
            .first()
        )
        user_id = user.id if user else None

        result = db.execute(
            text(
                "INSERT INTO cash_transactions "
                "(transaction_type, amount, balance_before, balance_after, description, created_by, created_at) "
                "VALUES (:type, :amount, :balance_before, :balance_after, :description, :created_by, NOW()) "
                "RETURNING id, transaction_type, amount, balance_before, balance_after, "
                "reference_type, reference_id, description, created_by, created_at"
            ),
            {
                "type": "deposit",
                "amount": float(deposit.amount),
                "balance_before": balance_before,
                "balance_after": balance_after,
                "description": deposit.description or "إضافة رأس مال",
                "created_by": user_id,
            },
        )

        db.commit()
        row = result.fetchone()

        log_activity(
            db, current_user, "deposit", "cash", None, None, f"إيداع {deposit.amount} EGP"
        )

        return {
            "id": row[0],
            "transaction_type": row[1],
            "amount": float(row[2]),
            "balance_before": float(row[3]),
            "balance_after": float(row[4]),
            "reference_type": row[5],
            "reference_id": row[6],
            "description": row[7],
            "created_by": row[8],
            "created_by_name": user.full_name if user else None,
            "created_at": row[9],
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"فشل في إيداع المبلغ: {str(e)}")


@router.post("/withdraw", response_model=schemas.CashTransactionResponse)
def withdraw_cash(
    withdrawal: schemas.CashWithdraw,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Withdraw cash/capital."""
    try:
        balance_result = db.execute(
            text(
                "SELECT balance_after FROM cash_transactions "
                "ORDER BY created_at DESC LIMIT 1"
            )
        ).fetchone()

        balance_before = float(balance_result[0]) if balance_result else 0.0

        if balance_before < float(withdrawal.amount):
            raise HTTPException(
                status_code=400,
                detail=f"الرصيد غير كافٍ. الرصيد المتاح: {balance_before} EGP",
            )

        balance_after = balance_before - float(withdrawal.amount)

        user = (
            db.query(models.User)
            .filter(models.User.username == current_user.username)
            .first()
        )
        user_id = user.id if user else None

        result = db.execute(
            text(
                "INSERT INTO cash_transactions "
                "(transaction_type, amount, balance_before, balance_after, description, created_by, created_at) "
                "VALUES (:type, :amount, :balance_before, :balance_after, :description, :created_by, NOW()) "
                "RETURNING id, transaction_type, amount, balance_before, balance_after, "
                "reference_type, reference_id, description, created_by, created_at"
            ),
            {
                "type": "withdraw",
                "amount": float(withdrawal.amount),
                "balance_before": balance_before,
                "balance_after": balance_after,
                "description": withdrawal.description or "سحب رأس مال",
                "created_by": user_id,
            },
        )

        db.commit()
        row = result.fetchone()

        log_activity(
            db, current_user, "withdraw", "cash", None, None, f"سحب {withdrawal.amount} EGP"
        )

        return {
            "id": row[0],
            "transaction_type": row[1],
            "amount": float(row[2]),
            "balance_before": float(row[3]),
            "balance_after": float(row[4]),
            "reference_type": row[5],
            "reference_id": row[6],
            "description": row[7],
            "created_by": row[8],
            "created_by_name": user.full_name if user else None,
            "created_at": row[9],
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"فشل في سحب المبلغ: {str(e)}")
