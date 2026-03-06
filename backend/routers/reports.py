"""
Advanced Reporting router (5.21-5.24)
- Hourly Sales Heatmap
- Dead Stock Report
- Profit Margin per Product / Category
- Cashier Performance Report
- Reorder Alerts (5.13)
"""
from typing import List, Optional
from datetime import date, timedelta
from decimal import Decimal
from collections import defaultdict

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/reports", tags=["Advanced Reports"])


# ============================================
# 5.21 — HOURLY SALES HEATMAP
# ============================================
@router.get("/hourly-heatmap", response_model=List[schemas.HourlySalesItem])
def get_hourly_sales_heatmap(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Get sales distribution by hour-of-day."""
    start = date.today() - timedelta(days=days)
    sales = (
        db.query(models.Sale)
        .filter(models.Sale.sale_date >= start, models.Sale.is_held == False)
        .all()
    )

    hourly: dict[int, dict] = defaultdict(lambda: {"count": 0, "total": Decimal("0")})
    for s in sales:
        hour = s.created_at.hour if s.created_at else 12
        hourly[hour]["count"] += 1
        hourly[hour]["total"] += s.total

    return [
        schemas.HourlySalesItem(
            hour=h,
            sales_count=hourly[h]["count"],
            total_amount=hourly[h]["total"],
        )
        for h in range(24)
    ]


# ============================================
# 5.22 — DEAD STOCK REPORT
# ============================================
@router.get("/dead-stock", response_model=List[schemas.DeadStockItem])
def get_dead_stock(
    days: int = Query(90, ge=7, le=730, description="Days without a sale"),
    db: Session = Depends(get_db),
):
    """Products that haven't been sold in N days."""
    cutoff = date.today() - timedelta(days=days)

    # Get last sale date per product
    last_sale_subq = (
        db.query(
            models.SaleItem.product_id,
            func.max(models.Sale.sale_date).label("last_sale"),
        )
        .join(models.Sale, models.SaleItem.sale_id == models.Sale.id)
        .group_by(models.SaleItem.product_id)
        .subquery()
    )

    products = (
        db.query(
            models.Product.id,
            models.Product.code,
            models.Product.name,
            models.Product.quantity,
            last_sale_subq.c.last_sale,
        )
        .outerjoin(last_sale_subq, models.Product.id == last_sale_subq.c.product_id)
        .filter(
            models.Product.is_active == True,
            models.Product.quantity > 0,
            (last_sale_subq.c.last_sale == None) | (last_sale_subq.c.last_sale <= cutoff),
        )
        .all()
    )

    result = []
    for p in products:
        days_since = (date.today() - p.last_sale).days if p.last_sale else 9999
        result.append(schemas.DeadStockItem(
            id=p.id,
            code=p.code,
            name=p.name,
            quantity=p.quantity,
            last_sale_date=p.last_sale,
            days_without_sale=days_since,
        ))

    return sorted(result, key=lambda x: x.days_without_sale, reverse=True)


# ============================================
# 5.23 — PROFIT MARGIN PER PRODUCT / CATEGORY
# ============================================
@router.get("/margins", response_model=List[schemas.ProductMarginItem])
def get_product_margins(
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Profit margin report per product with COGS."""
    query = db.query(models.Product).options(joinedload(models.Product.category))
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    products = query.filter(models.Product.is_active == True).all()

    # Aggregate sales
    sales_data = (
        db.query(
            models.SaleItem.product_id,
            func.sum(models.SaleItem.quantity).label("total_sold"),
            func.sum(models.SaleItem.total).label("total_revenue"),
        )
        .group_by(models.SaleItem.product_id)
        .all()
    )
    sales_map = {r.product_id: r for r in sales_data}

    result = []
    for p in products:
        margin = p.sale_price - p.purchase_price
        margin_pct = (margin / p.sale_price * 100) if p.sale_price > 0 else Decimal("0")

        sd = sales_map.get(p.id)
        total_sold = sd.total_sold if sd else 0
        total_revenue = sd.total_revenue if sd else Decimal("0")
        total_profit = total_revenue - (p.purchase_price * total_sold) if total_sold else Decimal("0")

        result.append(schemas.ProductMarginItem(
            id=p.id,
            code=p.code,
            name=p.name,
            category=p.category.name_ar if p.category else None,
            purchase_price=p.purchase_price,
            sale_price=p.sale_price,
            margin=margin,
            margin_percent=round(margin_pct, 2),
            total_sold=total_sold,
            total_revenue=total_revenue,
            total_profit=total_profit,
        ))
    return sorted(result, key=lambda x: x.total_profit, reverse=True)


# ============================================
# 5.24 — CASHIER PERFORMANCE REPORT
# ============================================
@router.get("/cashier-performance", response_model=List[schemas.CashierPerformanceItem])
def get_cashier_performance(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    """Performance metrics per cashier/user."""
    sales_q = db.query(
        models.Sale.created_by,
        func.count(models.Sale.id).label("sales_count"),
        func.coalesce(func.sum(models.Sale.total), 0).label("total_sales"),
    ).filter(models.Sale.is_held == False)

    if from_date:
        sales_q = sales_q.filter(models.Sale.sale_date >= from_date)
    if to_date:
        sales_q = sales_q.filter(models.Sale.sale_date <= to_date)

    sales_data = sales_q.group_by(models.Sale.created_by).all()

    returns_q = db.query(
        models.SaleReturn.created_by,
        func.count(models.SaleReturn.id).label("returns_count"),
        func.coalesce(func.sum(models.SaleReturn.total), 0).label("total_returns"),
    )
    if from_date:
        returns_q = returns_q.filter(models.SaleReturn.return_date >= from_date)
    if to_date:
        returns_q = returns_q.filter(models.SaleReturn.return_date <= to_date)
    returns_data = {r[0]: r for r in returns_q.group_by(models.SaleReturn.created_by).all()}

    users = {u.id: u for u in db.query(models.User).all()}

    result = []
    for row in sales_data:
        user = users.get(row[0])
        if not user:
            continue
        total = float(row.total_sales)
        count = row.sales_count
        ret = returns_data.get(row[0])
        result.append(schemas.CashierPerformanceItem(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            sales_count=count,
            total_sales=Decimal(str(total)),
            average_sale=Decimal(str(round(total / count, 2))) if count > 0 else Decimal("0"),
            returns_count=ret.returns_count if ret else 0,
            total_returns=ret.total_returns if ret else Decimal("0"),
        ))
    return sorted(result, key=lambda x: x.total_sales, reverse=True)


# ============================================
# 5.13 — REORDER POINT ALERTS + AUTO PO DRAFT
# ============================================
@router.get("/reorder-alerts")
def get_reorder_alerts(db: Session = Depends(get_db)):
    """Products at or below their reorder point."""
    products = (
        db.query(models.Product)
        .options(joinedload(models.Product.category), joinedload(models.Product.supplier))
        .filter(
            models.Product.is_active == True,
            models.Product.quantity <= models.Product.min_quantity,
        )
        .all()
    )
    return [
        {
            "id": p.id,
            "code": p.code,
            "name": p.name,
            "category": p.category.name_ar if p.category else None,
            "supplier_id": p.supplier_id,
            "supplier_name": p.supplier.name if p.supplier else None,
            "current_quantity": p.quantity,
            "min_quantity": p.min_quantity,
            "reorder_point": p.reorder_point,
            "suggested_order": max(p.min_quantity * 2 - p.quantity, 0),
        }
        for p in products
    ]


@router.post("/auto-po-draft")
def generate_auto_po_draft(db: Session = Depends(get_db)):
    """Generate purchase order drafts for products needing reorder, grouped by supplier."""
    products = (
        db.query(models.Product)
        .filter(
            models.Product.is_active == True,
            models.Product.quantity <= models.Product.min_quantity,
            models.Product.supplier_id != None,
        )
        .all()
    )

    by_supplier: dict[int, list] = defaultdict(list)
    for p in products:
        suggested = max(p.min_quantity * 2 - p.quantity, 0)
        if suggested > 0:
            by_supplier[p.supplier_id].append({
                "product_id": p.id,
                "product_name": p.name,
                "current_quantity": p.quantity,
                "suggested_quantity": suggested,
                "unit_price": float(p.purchase_price),
                "estimated_total": float(p.purchase_price * suggested),
            })

    drafts = []
    for supplier_id, items in by_supplier.items():
        supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
        drafts.append({
            "supplier_id": supplier_id,
            "supplier_name": supplier.name if supplier else None,
            "items": items,
            "estimated_total": sum(i["estimated_total"] for i in items),
        })
    return {"drafts": drafts, "total_items": sum(len(d["items"]) for d in drafts)}
