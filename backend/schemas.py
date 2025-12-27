"""
Pydantic Schemas for API Request/Response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


# ============================================
# CATEGORY SCHEMAS
# ============================================
class CategoryBase(BaseModel):
    code: str
    name: str
    name_ar: Optional[str] = None
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    name_ar: Optional[str] = None
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# SUPPLIER SCHEMAS
# ============================================
class SupplierBase(BaseModel):
    code: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class SupplierResponse(SupplierBase):
    id: int
    total_purchases: Decimal = Decimal("0")
    balance: Decimal = Decimal("0")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# CUSTOMER SCHEMAS
# ============================================
class CustomerBase(BaseModel):
    code: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: int
    total_purchases: Decimal = Decimal("0")
    balance: Decimal = Decimal("0")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# PRODUCT SCHEMAS
# ============================================
class ProductBase(BaseModel):
    code: str
    name: str
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    purchase_price: Decimal = Decimal("0")
    sale_price: Decimal = Decimal("0")
    quantity: int = 0
    min_quantity: int = 5
    description: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    purchase_price: Optional[Decimal] = None
    sale_price: Optional[Decimal] = None
    quantity: Optional[int] = None
    min_quantity: Optional[int] = None
    description: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    category: Optional[CategoryResponse] = None
    supplier: Optional[SupplierResponse] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductSimple(BaseModel):
    id: int
    code: str
    name: str
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    purchase_price: Decimal
    sale_price: Decimal
    quantity: int
    min_quantity: int
    description: Optional[str] = None
    supplier: Optional[str] = None
    category: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================
# SALE ITEM SCHEMAS
# ============================================
class SaleItemBase(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    total: Decimal


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: Optional[Decimal] = None


class SaleItemResponse(SaleItemBase):
    id: int
    sale_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# SALE SCHEMAS
# ============================================
class SaleBase(BaseModel):
    customer_id: Optional[int] = None
    customer_name: Optional[str] = "عميل نقدي"
    sale_date: Optional[date] = None
    discount: Decimal = Decimal("0")
    paid: Decimal = Decimal("0")
    notes: Optional[str] = None


class SaleCreate(SaleBase):
    items: List[SaleItemCreate]


class SaleResponse(BaseModel):
    id: int
    invoice_no: str
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    sale_date: date
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    paid: Decimal
    remaining: Decimal
    status: str
    notes: Optional[str] = None
    items: List[SaleItemResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# PURCHASE ITEM SCHEMAS
# ============================================
class PurchaseItemBase(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    total: Decimal


class PurchaseItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal


class PurchaseItemResponse(PurchaseItemBase):
    id: int
    purchase_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# PURCHASE SCHEMAS
# ============================================
class PurchaseBase(BaseModel):
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
    purchase_date: Optional[date] = None
    discount: Decimal = Decimal("0")
    paid: Decimal = Decimal("0")
    notes: Optional[str] = None


class PurchaseCreate(PurchaseBase):
    items: List[PurchaseItemCreate]


class PurchaseResponse(BaseModel):
    id: int
    invoice_no: str
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
    purchase_date: date
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    paid: Decimal
    remaining: Decimal
    status: str
    notes: Optional[str] = None
    items: List[PurchaseItemResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# INVENTORY MOVEMENT SCHEMAS
# ============================================
class InventoryAdjustment(BaseModel):
    product_id: int
    adjustment_type: str  # 'add', 'subtract', 'set'
    quantity: int
    reason: Optional[str] = None
    notes: Optional[str] = None


class InventoryMovementResponse(BaseModel):
    id: int
    product_id: int
    movement_type: str
    quantity_before: int
    quantity_change: int
    quantity_after: int
    reason: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# SETTINGS SCHEMAS
# ============================================
class SettingUpdate(BaseModel):
    key: str
    value: str


class SettingsUpdate(BaseModel):
    settings: List[SettingUpdate]


class SettingResponse(BaseModel):
    key: str
    value: Optional[str] = None
    description: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# DASHBOARD SCHEMAS
# ============================================
class DashboardStats(BaseModel):
    total_sales: Decimal
    total_products: int
    total_customers: int
    today_profit: Decimal
    low_stock_count: int


class LowStockProduct(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    quantity: int
    min_quantity: int
    status: str


class ProfitReport(BaseModel):
    total_sales: Decimal
    total_cost: Decimal
    gross_profit: Decimal
    total_discount: Decimal
    net_profit: Decimal
    sales_count: int


# ============================================
# ANALYTICS SCHEMAS
# ============================================
class SalesTrendItem(BaseModel):
    date: str
    sales: Decimal
    profit: Decimal
    orders: int


class SalesTrendReport(BaseModel):
    data: List[SalesTrendItem]
    period: str  # 'daily', 'weekly', 'monthly'


class TopProductItem(BaseModel):
    id: int
    name: str
    quantity_sold: int
    revenue: Decimal
    profit: Decimal


class InventoryValueReport(BaseModel):
    total_items: int
    total_quantity: int
    total_cost_value: Decimal
    total_sale_value: Decimal
    potential_profit: Decimal
    stock_health: dict  # {'good': count, 'low': count, 'out': count}


class CustomerAnalyticsItem(BaseModel):
    id: int
    name: str
    total_purchases: Decimal
    orders_count: int
    balance: Decimal
    last_purchase: Optional[date] = None


class BusinessKPIs(BaseModel):
    # Revenue Metrics
    total_revenue: Decimal
    today_revenue: Decimal
    this_week_revenue: Decimal
    this_month_revenue: Decimal
    
    # Profit Metrics
    gross_profit_margin: Decimal  # (gross_profit / revenue) * 100
    net_profit_margin: Decimal    # (net_profit / revenue) * 100
    
    # Operations
    average_order_value: Decimal
    total_orders: int
    pending_receivables: Decimal  # Total unpaid customer balances
    pending_payables: Decimal     # Total unpaid supplier balances
    
    # Inventory
    inventory_value: Decimal
    inventory_items: int
    low_stock_items: int
    out_of_stock_items: int
    
    # Growth (compared to previous period)
    revenue_growth: Decimal  # percentage
    orders_growth: Decimal   # percentage

