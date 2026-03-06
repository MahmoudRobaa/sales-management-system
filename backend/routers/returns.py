"""
Sales Returns / Refunds router (5.5)
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
import crud
import cache
from auth import get_current_user, require_manager, TokenData
from routers.deps import log_activity

router = APIRouter(prefix="/api/returns", tags=["Sales Returns"])


@router.get("", response_model=List[schemas.SaleReturnResponse])
def list_returns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    returns = (
        db.query(models.SaleReturn)
        .order_by(models.SaleReturn.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    result = []
    for r in returns:
        items_resp = [
            schemas.SaleReturnItemResponse(
                id=i.id, return_id=i.return_id, product_id=i.product_id,
                product_name=i.product_name, quantity=i.quantity,
                unit_price=i.unit_price, total=i.total, reason=i.reason,
                created_at=i.created_at,
            )
            for i in r.items
        ]
        result.append(schemas.SaleReturnResponse(
            id=r.id, return_no=r.return_no, sale_id=r.sale_id,
            sale_invoice_no=r.sale_invoice_no, customer_id=r.customer_id,
            customer_name=r.customer_name, return_date=r.return_date,
            subtotal=r.subtotal, tax_amount=r.tax_amount, total=r.total,
            refund_method=r.refund_method, refund_amount=r.refund_amount,
            reason=r.reason, status=r.status, restock=r.restock,
            notes=r.notes, items=items_resp, created_at=r.created_at,
        ))
    return result


@router.get("/{return_id}", response_model=schemas.SaleReturnResponse)
def get_return(return_id: int, db: Session = Depends(get_db)):
    r = db.query(models.SaleReturn).filter(models.SaleReturn.id == return_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Return not found")
    return r


@router.post("", response_model=schemas.SaleReturnResponse)
def create_return(
    data: schemas.SaleReturnCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Create a sales return / refund with optional restocking."""
    from decimal import Decimal

    sale = crud.get_sale(db, data.sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    # Generate return number
    count = db.query(models.SaleReturn).count()
    return_no = f"RET{str(count + 1).zfill(4)}"

    user = db.query(models.User).filter(models.User.username == current_user.username).first()
    user_id = user.id if user else None

    subtotal = Decimal("0")
    return_items = []

    for item in data.items:
        product = crud.get_product(db, item.product_id)
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")

        item_total = item.unit_price * item.quantity
        subtotal += item_total

        return_items.append({
            'product_id': item.product_id,
            'product_name': product.name,
            'quantity': item.quantity,
            'unit_price': item.unit_price,
            'total': item_total,
            'reason': item.reason,
        })

    tax_amount = (subtotal * sale.tax_rate / Decimal("100")).quantize(Decimal("0.01")) if sale.tax_rate else Decimal("0")
    total = subtotal + tax_amount

    db_return = models.SaleReturn(
        return_no=return_no,
        sale_id=sale.id,
        sale_invoice_no=sale.invoice_no,
        customer_id=sale.customer_id,
        customer_name=sale.customer_name,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total=total,
        refund_method=data.refund_method,
        refund_amount=total,
        reason=data.reason,
        status="completed",
        restock=data.restock,
        notes=data.notes,
        created_by=user_id,
    )
    db.add(db_return)
    db.flush()

    for item_data in return_items:
        db_item = models.SaleReturnItem(return_id=db_return.id, **item_data)
        db.add(db_item)

        # Restock if requested
        if data.restock:
            product = crud.get_product(db, item_data['product_id'])
            if product:
                qty_before = product.quantity
                product.quantity += item_data['quantity']
                movement = models.InventoryMovement(
                    product_id=product.id,
                    movement_type='return',
                    quantity_before=qty_before,
                    quantity_change=item_data['quantity'],
                    quantity_after=product.quantity,
                    reason='sale_return',
                    reference_type='return',
                    reference_id=db_return.id,
                )
                db.add(movement)

    # Update customer balance
    if sale.customer_id:
        customer = crud.get_customer(db, sale.customer_id)
        if customer:
            customer.total_purchases = max(Decimal("0"), customer.total_purchases - total)
            if data.refund_method == "credit":
                customer.balance = max(Decimal("0"), customer.balance - total)

    cache.invalidate_pattern("dashboard:*")
    cache.invalidate_pattern("analytics:*")

    db.commit()
    db.refresh(db_return)

    log_activity(db, current_user, "create", "return", db_return.id, f"مرتجع #{return_no}")
    return db_return


@router.put("/{return_id}/approve")
def approve_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_manager),
):
    """Approve a pending return (manager only)."""
    r = db.query(models.SaleReturn).filter(models.SaleReturn.id == return_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Return not found")
    if r.status != "pending":
        raise HTTPException(status_code=400, detail="Return is not pending")

    user = db.query(models.User).filter(models.User.username == current_user.username).first()
    r.status = "approved"
    r.approved_by = user.id if user else None
    db.commit()

    log_activity(db, current_user, "approve", "return", return_id, f"اعتماد مرتجع #{r.return_no}")
    return {"message": "Return approved"}
