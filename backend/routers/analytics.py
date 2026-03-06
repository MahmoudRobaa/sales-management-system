"""
Analytics & Dashboard router — KPIs, trends, reports.
"""
from typing import List, Optional
from datetime import date, timedelta
from collections import defaultdict

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
import crud
from auth import require_manager, TokenData

router = APIRouter(tags=["Analytics"])


# ============================================
# DASHBOARD
# ============================================
@router.get("/api/dashboard/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)


@router.get("/api/dashboard/low-stock", response_model=List[schemas.LowStockProduct])
def get_low_stock_products(db: Session = Depends(get_db)):
    return crud.get_low_stock_products(db)


@router.get("/api/reports/profit", response_model=schemas.ProfitReport)
def get_profit_report(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    return crud.get_profit_report(db, from_date=from_date, to_date=to_date)


# ============================================
# ANALYTICS
# ============================================
@router.get("/api/analytics/sales-trend", response_model=schemas.SalesTrendReport)
def get_sales_trend(period: str = "daily", days: int = 30, db: Session = Depends(get_db)):
    """Get sales trend data for charts."""
    return crud.get_sales_trend(db, period=period, days=days)


@router.get("/api/analytics/top-products", response_model=List[schemas.TopProductItem])
def get_top_products(limit: int = 10, db: Session = Depends(get_db)):
    """Get top selling products by revenue."""
    return crud.get_top_products(db, limit=limit)


@router.get("/api/analytics/inventory-value", response_model=schemas.InventoryValueReport)
def get_inventory_value(db: Session = Depends(get_db)):
    """Get inventory value and stock health metrics."""
    return crud.get_inventory_value(db)


@router.get("/api/analytics/kpis", response_model=schemas.BusinessKPIs)
def get_business_kpis(db: Session = Depends(get_db)):
    """Get comprehensive business KPIs."""
    return crud.get_business_kpis(db)


@router.get("/api/analytics/top-customers", response_model=List[schemas.CustomerAnalyticsItem])
def get_top_customers(limit: int = 10, db: Session = Depends(get_db)):
    """Get top customers by purchase amount."""
    return crud.get_top_customers(db, limit=limit)


@router.get("/api/analytics/financial-reports")
def get_financial_reports(
    period: str = Query("month", regex="^(week|month|3months|6months|year)$"),
    db: Session = Depends(get_db),
):
    """Get financial reports with Sales, Purchases, and Profit data."""
    today = date.today()
    if period == "week":
        start_date = today - timedelta(days=7)
        group_by = "day"
    elif period == "month":
        start_date = today - timedelta(days=30)
        group_by = "day"
    elif period == "3months":
        start_date = today - timedelta(days=90)
        group_by = "week"
    elif period == "6months":
        start_date = today - timedelta(days=180)
        group_by = "week"
    else:  # year
        start_date = today - timedelta(days=365)
        group_by = "month"

    sales = (
        db.query(models.Sale)
        .filter(models.Sale.sale_date >= start_date, models.Sale.sale_date <= today)
        .all()
    )
    purchases = (
        db.query(models.Purchase)
        .filter(
            models.Purchase.purchase_date >= start_date,
            models.Purchase.purchase_date <= today,
        )
        .all()
    )

    total_sales = float(sum(s.total for s in sales) or 0)
    total_purchases = float(sum(p.total for p in purchases) or 0)
    net_profit = total_sales - total_purchases

    gross_profit = 0.0
    for sale in sales:
        for item in sale.items:
            cost = float(item.product.purchase_price) * item.quantity if item.product else 0
            gross_profit += float(item.total) - cost

    sales_by_date: dict[str, float] = defaultdict(float)
    purchases_by_date: dict[str, float] = defaultdict(float)
    profit_by_date: dict[str, float] = defaultdict(float)

    def _date_key(d: date, gb: str) -> str:
        if gb == "day":
            return d.strftime("%Y-%m-%d")
        elif gb == "week":
            iso_year, iso_week, _ = d.isocalendar()
            return f"{iso_year}-W{iso_week:02d}"
        return d.strftime("%Y-%m")

    for sale in sales:
        key = _date_key(sale.sale_date, group_by)
        sales_by_date[key] += float(sale.total)
        sale_profit = 0.0
        for item in sale.items:
            cost = float(item.product.purchase_price) * item.quantity if item.product else 0
            sale_profit += float(item.total) - cost
        profit_by_date[key] += sale_profit

    for purchase in purchases:
        key = _date_key(purchase.purchase_date, group_by)
        purchases_by_date[key] += float(purchase.total)

    all_dates = sorted(set(list(sales_by_date.keys()) + list(purchases_by_date.keys())))
    trend_data = [
        {
            "date": d,
            "sales": round(sales_by_date.get(d, 0), 2),
            "purchases": round(purchases_by_date.get(d, 0), 2),
            "profit": round(profit_by_date.get(d, 0), 2),
        }
        for d in all_dates
    ]

    profit_margin = (gross_profit / total_sales * 100) if total_sales > 0 else 0

    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": today.isoformat(),
        "summary": {
            "total_sales": round(total_sales, 2),
            "total_purchases": round(total_purchases, 2),
            "gross_profit": round(gross_profit, 2),
            "net_profit": round(net_profit, 2),
            "profit_margin": round(profit_margin, 2),
            "sales_count": len(sales),
            "purchases_count": len(purchases),
        },
        "trend_data": trend_data,
    }


# ============================================
# ACTIVITY LOGS (Admin/Manager)
# ============================================
@router.get("/api/activity-logs")
def get_activity_logs(
    skip: int = 0,
    limit: int = 100,
    entity_type: Optional[str] = None,
    current_user: TokenData = Depends(require_manager),
    db: Session = Depends(get_db),
):
    """Get activity logs (admin/manager only)."""
    query = db.query(models.ActivityLog).order_by(models.ActivityLog.created_at.desc())
    if entity_type:
        query = query.filter(models.ActivityLog.entity_type == entity_type)
    return query.offset(skip).limit(limit).all()
