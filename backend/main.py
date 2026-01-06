"""
Sales Management System - FastAPI Backend
نظام إدارة المبيعات - الواجهة الخلفية
"""
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
import csv
import io

from database import get_db, engine
import models
import schemas
import crud

# Create database tables (if not exists)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sales Management System API",
    description="نظام إدارة المبيعات - API",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# ROOT ENDPOINT
# ============================================
@app.get("/")
def read_root():
    return {"message": "Sales Management System API", "version": "1.0.0"}


# ============================================
# CATEGORY ENDPOINTS
# ============================================
@app.get("/api/categories", response_model=List[schemas.CategoryResponse])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_categories(db, skip=skip, limit=limit)


@app.get("/api/categories/{category_id}", response_model=schemas.CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = crud.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@app.post("/api/categories", response_model=schemas.CategoryResponse)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    existing = crud.get_category_by_code(db, category.code)
    if existing:
        raise HTTPException(status_code=400, detail="Category code already exists")
    return crud.create_category(db, category)


@app.put("/api/categories/{category_id}", response_model=schemas.CategoryResponse)
def update_category(category_id: int, category: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    updated = crud.update_category(db, category_id, category)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated


@app.delete("/api/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    if not crud.delete_category(db, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}


# ============================================
# SUPPLIER ENDPOINTS
# ============================================
@app.get("/api/suppliers", response_model=List[schemas.SupplierResponse])
def get_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_suppliers(db, skip=skip, limit=limit)


# NOTE: generate-code must come BEFORE {supplier_id} to avoid route conflict
@app.get("/api/suppliers/generate-code", response_model=dict)
def generate_supplier_code(db: Session = Depends(get_db)):
    return {"code": crud.generate_supplier_code(db)}


@app.get("/api/suppliers/{supplier_id}", response_model=schemas.SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = crud.get_supplier(db, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@app.post("/api/suppliers", response_model=schemas.SupplierResponse)
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    existing = crud.get_supplier_by_code(db, supplier.code)
    if existing:
        raise HTTPException(status_code=400, detail="Supplier code already exists")
    return crud.create_supplier(db, supplier)


@app.put("/api/suppliers/{supplier_id}", response_model=schemas.SupplierResponse)
def update_supplier(supplier_id: int, supplier: schemas.SupplierUpdate, db: Session = Depends(get_db)):
    updated = crud.update_supplier(db, supplier_id, supplier)
    if not updated:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return updated


@app.delete("/api/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    if not crud.delete_supplier(db, supplier_id):
        raise HTTPException(status_code=404, detail="Supplier not found")
    return {"message": "Supplier deleted successfully"}


# ============================================
# CUSTOMER ENDPOINTS
# ============================================
@app.get("/api/customers", response_model=List[schemas.CustomerResponse])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_customers(db, skip=skip, limit=limit)


# NOTE: generate-code must come BEFORE {customer_id} to avoid route conflict
@app.get("/api/customers/generate-code", response_model=dict)
def generate_customer_code(db: Session = Depends(get_db)):
    return {"code": crud.generate_customer_code(db)}


@app.get("/api/customers/{customer_id}", response_model=schemas.CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.post("/api/customers", response_model=schemas.CustomerResponse)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    existing = crud.get_customer_by_code(db, customer.code)
    if existing:
        raise HTTPException(status_code=400, detail="Customer code already exists")
    return crud.create_customer(db, customer)


@app.put("/api/customers/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(customer_id: int, customer: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    updated = crud.update_customer(db, customer_id, customer)
    if not updated:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated


@app.delete("/api/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    if not crud.delete_customer(db, customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}


# ============================================
# PRODUCT ENDPOINTS
# ============================================
@app.get("/api/products", response_model=List[schemas.ProductSimple])
def get_products(
    skip: int = 0, 
    limit: int = 100, 
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_products_with_details(db, skip=skip, limit=limit, category=category)


# NOTE: generate-code must come BEFORE {product_id} to avoid route conflict
@app.get("/api/products/generate-code", response_model=dict)
def generate_product_code(db: Session = Depends(get_db)):
    return {"code": crud.generate_product_code(db)}


@app.get("/api/products/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/api/products", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    existing = crud.get_product_by_code(db, product.code)
    if existing:
        raise HTTPException(status_code=400, detail="Product code already exists")
    return crud.create_product(db, product)


@app.put("/api/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    updated = crud.update_product(db, product_id, product)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated


@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    if not crud.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}


# ============================================
# PRODUCTS CSV IMPORT/EXPORT
# ============================================
@app.get("/api/products/export-csv")
def export_products_csv(db: Session = Depends(get_db)):
    """Export all products to CSV with UTF-8 BOM for Arabic Excel support"""
    products = crud.get_products_with_details(db, skip=0, limit=10000)
    
    # Create CSV in memory with BOM for Excel Arabic support
    output = io.StringIO()
    output.write('\ufeff')  # UTF-8 BOM for Excel
    
    writer = csv.writer(output)
    # Header row
    writer.writerow([
        'Code', 'Name', 'Category', 'Supplier', 'Purchase Price', 
        'Sale Price', 'Quantity', 'Min Quantity', 'Description'
    ])
    
    # Data rows
    for p in products:
        writer.writerow([
            p.get('code', ''),
            p.get('name', ''),
            p.get('category', ''),
            p.get('supplier', ''),
            p.get('purchase_price', 0),
            p.get('sale_price', 0),
            p.get('quantity', 0),
            p.get('min_quantity', 5),
            p.get('description', '')
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=products_export.csv"
        }
    )


@app.post("/api/products/import-csv")
async def import_products_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import products from CSV file with validation"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    content = await file.read()
    
    # Try different encodings
    for encoding in ['utf-8-sig', 'utf-8', 'cp1256', 'iso-8859-6']:
        try:
            decoded = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise HTTPException(status_code=400, detail="Could not decode file. Please use UTF-8 encoding.")
    
    reader = csv.DictReader(io.StringIO(decoded))
    
    imported = 0
    errors = []
    
    for row_num, row in enumerate(reader, start=2):
        try:
            # Get values with flexible column names
            code = row.get('Code') or row.get('code') or row.get('الكود') or ''
            name = row.get('Name') or row.get('name') or row.get('الاسم') or ''
            purchase_price = row.get('Purchase Price') or row.get('purchase_price') or row.get('سعر الشراء') or '0'
            sale_price = row.get('Sale Price') or row.get('sale_price') or row.get('سعر البيع') or '0'
            quantity = row.get('Quantity') or row.get('quantity') or row.get('الكمية') or '0'
            min_quantity = row.get('Min Quantity') or row.get('min_quantity') or row.get('الحد الأدنى') or '5'
            description = row.get('Description') or row.get('description') or row.get('الوصف') or ''
            
            # Validation
            if not code.strip():
                errors.append(f"Row {row_num}: Code is required")
                continue
            if not name.strip():
                errors.append(f"Row {row_num}: Name is required")
                continue
            
            # Check for duplicate code
            existing = crud.get_product_by_code(db, code.strip())
            if existing:
                errors.append(f"Row {row_num}: Code '{code}' already exists")
                continue
            
            # Create product
            product_data = schemas.ProductCreate(
                code=code.strip(),
                name=name.strip(),
                purchase_price=float(purchase_price) if purchase_price else 0,
                sale_price=float(sale_price) if sale_price else 0,
                quantity=int(float(quantity)) if quantity else 0,
                min_quantity=int(float(min_quantity)) if min_quantity else 5,
                description=description.strip() if description else None
            )
            crud.create_product(db, product_data)
            imported += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    return {
        "imported": imported,
        "errors": errors[:20],  # Limit errors to first 20
        "total_errors": len(errors)
    }


# ============================================
# SALE ENDPOINTS
# ============================================
@app.get("/api/sales", response_model=List[schemas.SaleResponse])
def get_sales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_sales(db, skip=skip, limit=limit)


@app.get("/api/sales/{sale_id}", response_model=schemas.SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = crud.get_sale(db, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


@app.post("/api/sales", response_model=schemas.SaleResponse)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_sale(db, sale)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/sales/{sale_id}")
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    if not crud.delete_sale(db, sale_id):
        raise HTTPException(status_code=404, detail="Sale not found")
    return {"message": "Sale deleted successfully"}


# ============================================
# PURCHASE ENDPOINTS
# ============================================
@app.get("/api/purchases", response_model=List[schemas.PurchaseResponse])
def get_purchases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_purchases(db, skip=skip, limit=limit)


@app.get("/api/purchases/{purchase_id}", response_model=schemas.PurchaseResponse)
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    purchase = crud.get_purchase(db, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return purchase


@app.post("/api/purchases", response_model=schemas.PurchaseResponse)
def create_purchase(purchase: schemas.PurchaseCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_purchase(db, purchase)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/purchases/{purchase_id}")
def delete_purchase(purchase_id: int, db: Session = Depends(get_db)):
    if not crud.delete_purchase(db, purchase_id):
        raise HTTPException(status_code=404, detail="Purchase not found")
    return {"message": "Purchase deleted successfully"}


# ============================================
# INVENTORY ENDPOINTS
# ============================================
@app.get("/api/inventory/movements", response_model=List[schemas.InventoryMovementResponse])
def get_inventory_movements(
    product_id: Optional[int] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    return crud.get_inventory_movements(db, product_id=product_id, skip=skip, limit=limit)


@app.post("/api/inventory/adjust", response_model=schemas.InventoryMovementResponse)
def adjust_inventory(adjustment: schemas.InventoryAdjustment, db: Session = Depends(get_db)):
    try:
        return crud.adjust_inventory(db, adjustment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# SETTINGS ENDPOINTS
# ============================================
@app.get("/api/settings", response_model=List[schemas.SettingResponse])
def get_settings(db: Session = Depends(get_db)):
    return crud.get_settings(db)


@app.put("/api/settings", response_model=List[schemas.SettingResponse])
def update_settings(settings: schemas.SettingsUpdate, db: Session = Depends(get_db)):
    return crud.update_settings(db, settings.settings)


# ============================================
# DASHBOARD ENDPOINTS
# ============================================
@app.get("/api/dashboard/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)


@app.get("/api/dashboard/low-stock", response_model=List[schemas.LowStockProduct])
def get_low_stock_products(db: Session = Depends(get_db)):
    return crud.get_low_stock_products(db)


@app.get("/api/reports/profit", response_model=schemas.ProfitReport)
def get_profit_report(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    return crud.get_profit_report(db, from_date=from_date, to_date=to_date)


# ============================================
# ANALYTICS ENDPOINTS
# ============================================
@app.get("/api/analytics/sales-trend", response_model=schemas.SalesTrendReport)
def get_sales_trend(
    period: str = 'daily',
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get sales trend data for charts"""
    return crud.get_sales_trend(db, period=period, days=days)


@app.get("/api/analytics/top-products", response_model=List[schemas.TopProductItem])
def get_top_products(limit: int = 10, db: Session = Depends(get_db)):
    """Get top selling products by revenue"""
    return crud.get_top_products(db, limit=limit)


@app.get("/api/analytics/inventory-value", response_model=schemas.InventoryValueReport)
def get_inventory_value(db: Session = Depends(get_db)):
    """Get inventory value and stock health metrics"""
    return crud.get_inventory_value(db)


@app.get("/api/analytics/kpis", response_model=schemas.BusinessKPIs)
def get_business_kpis(db: Session = Depends(get_db)):
    """Get comprehensive business KPIs"""
    return crud.get_business_kpis(db)


@app.get("/api/analytics/top-customers", response_model=List[schemas.CustomerAnalyticsItem])
def get_top_customers(limit: int = 10, db: Session = Depends(get_db)):
    """Get top customers by purchase amount"""
    return crud.get_top_customers(db, limit=limit)


@app.get("/api/analytics/financial-reports")
def get_financial_reports(
    period: str = Query('month', regex='^(week|month|3months|6months|year)$'),
    db: Session = Depends(get_db)
):
    """
    Get financial reports with Sales, Purchases, and Profit data
    period: week, month, 3months, 6months, year
    """
    # Calculate date range based on period
    today = date.today()
    if period == 'week':
        start_date = today - timedelta(days=7)
        group_by = 'day'
    elif period == 'month':
        start_date = today - timedelta(days=30)
        group_by = 'day'
    elif period == '3months':
        start_date = today - timedelta(days=90)
        group_by = 'week'
    elif period == '6months':
        start_date = today - timedelta(days=180)
        group_by = 'week'
    else:  # year
        start_date = today - timedelta(days=365)
        group_by = 'month'
    
    # Get all sales in period
    sales = db.query(models.Sale).filter(
        models.Sale.sale_date >= start_date,
        models.Sale.sale_date <= today
    ).all()
    
    # Get all purchases in period
    purchases = db.query(models.Purchase).filter(
        models.Purchase.purchase_date >= start_date,
        models.Purchase.purchase_date <= today
    ).all()
    
    # Calculate totals
    total_sales = float(sum(s.total for s in sales) or 0)
    total_purchases = float(sum(p.total for p in purchases) or 0)
    net_profit = total_sales - total_purchases
    
    # Calculate profit from sales (sale price - purchase price)
    gross_profit = 0.0
    for sale in sales:
        for item in sale.items:
            cost = float(item.product.purchase_price) * item.quantity if item.product else 0
            gross_profit += float(item.total) - cost
    
    # Group data for charts
    from collections import defaultdict
    sales_by_date = defaultdict(float)
    purchases_by_date = defaultdict(float)
    profit_by_date = defaultdict(float)
    
    def get_date_key(d, group_by):
        """Get grouping key for a date with proper ISO week handling"""
        if group_by == 'day':
            return d.strftime('%Y-%m-%d')
        elif group_by == 'week':
            # Use ISO week: %G is ISO year, %V is ISO week number (01-53)
            # This correctly handles year boundaries (e.g., Dec 31 could be week 1 of next year)
            iso_year, iso_week, _ = d.isocalendar()
            return f"{iso_year}-W{iso_week:02d}"
        else:
            return d.strftime('%Y-%m')
    
    for sale in sales:
        key = get_date_key(sale.sale_date, group_by)
        sales_by_date[key] += float(sale.total)
        
        # Calculate profit for this sale
        sale_profit = 0.0
        for item in sale.items:
            cost = float(item.product.purchase_price) * item.quantity if item.product else 0
            sale_profit += float(item.total) - cost
        profit_by_date[key] += sale_profit
    
    for purchase in purchases:
        key = get_date_key(purchase.purchase_date, group_by)
        purchases_by_date[key] += float(purchase.total)
    
    # Create sorted trend data
    all_dates = sorted(set(list(sales_by_date.keys()) + list(purchases_by_date.keys())))
    trend_data = []
    for d in all_dates:
        trend_data.append({
            'date': d,
            'sales': round(sales_by_date.get(d, 0), 2),
            'purchases': round(purchases_by_date.get(d, 0), 2),
            'profit': round(profit_by_date.get(d, 0), 2)
        })
    
    # Profit margin
    profit_margin = (gross_profit / total_sales * 100) if total_sales > 0 else 0
    
    return {
        'period': period,
        'start_date': start_date.isoformat(),
        'end_date': today.isoformat(),
        'summary': {
            'total_sales': round(total_sales, 2),
            'total_purchases': round(total_purchases, 2),
            'gross_profit': round(gross_profit, 2),
            'net_profit': round(net_profit, 2),
            'profit_margin': round(profit_margin, 2),
            'sales_count': len(sales),
            'purchases_count': len(purchases)
        },
        'trend_data': trend_data
    }


# ============================================
# HEALTH CHECK
# ============================================
@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

