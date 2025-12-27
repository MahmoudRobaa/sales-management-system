"""
Sales Management System - FastAPI Backend
نظام إدارة المبيعات - الواجهة الخلفية
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

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


# ============================================
# HEALTH CHECK
# ============================================
@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

