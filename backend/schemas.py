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
    credit_limit: Decimal = Decimal("0")


class CustomerUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: int
    total_purchases: Decimal = Decimal("0")
    balance: Decimal = Decimal("0")
    credit_limit: Decimal = Decimal("0")
    loyalty_points: int = 0
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
    tax_amount: Decimal = Decimal("0")
    total: Decimal
    variant_id: Optional[int] = None
    variant_label: Optional[str] = None


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: Optional[Decimal] = None
    variant_id: Optional[int] = None


class SaleItemResponse(SaleItemBase):
    id: int
    sale_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# SALE SCHEMAS
# ============================================
class SalePaymentCreate(BaseModel):
    payment_method: str  # cash, card, wallet
    amount: Decimal
    reference_no: Optional[str] = None
    notes: Optional[str] = None


class SalePaymentResponse(SalePaymentCreate):
    id: int
    sale_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SaleBase(BaseModel):
    customer_id: Optional[int] = None
    customer_name: Optional[str] = "عميل نقدي"
    sale_date: Optional[date] = None
    discount: Decimal = Decimal("0")
    tax_rate: Optional[Decimal] = None  # if None, use store setting
    paid: Decimal = Decimal("0")
    payment_method: Optional[str] = "كاش"
    is_held: bool = False
    held_name: Optional[str] = None
    shift_id: Optional[int] = None
    notes: Optional[str] = None
    payments: Optional[List[SalePaymentCreate]] = None


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
    tax_rate: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    total: Decimal
    paid: Decimal
    remaining: Decimal
    status: str
    payment_method: Optional[str] = None
    is_held: bool = False
    held_name: Optional[str] = None
    shift_id: Optional[int] = None
    notes: Optional[str] = None
    items: List[SaleItemResponse] = []
    payments: List[SalePaymentResponse] = []
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
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
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
    payment_method: Optional[str] = "كاش"
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
    payment_method: Optional[str] = None
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
    product_name: Optional[str] = None
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


# ============================================
# CASH TRANSACTION SCHEMAS
# ============================================
class CashDeposit(BaseModel):
    """Request schema for depositing capital"""
    amount: Decimal = Field(..., gt=0, description="Amount to deposit")
    description: Optional[str] = "إضافة رأس مال"


class CashWithdraw(BaseModel):
    """Request schema for withdrawing capital"""
    amount: Decimal = Field(..., gt=0, description="Amount to withdraw")
    description: Optional[str] = "سحب رأس مال"


class CashBalanceResponse(BaseModel):
    """Current cash balance"""
    balance: Decimal
    last_updated: Optional[datetime] = None


class CashTransactionResponse(BaseModel):
    """Response schema for cash transactions"""
    id: int
    transaction_type: str
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    description: Optional[str] = None
    created_by: Optional[int] = None
    created_by_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# PRODUCT VARIANT SCHEMAS (5.12)
# ============================================
class VariantCreate(BaseModel):
    sku: str
    name: str
    size: Optional[str] = None
    color: Optional[str] = None
    weight: Optional[str] = None
    purchase_price: Decimal = Decimal("0")
    sale_price: Decimal = Decimal("0")
    quantity: int = 0
    barcode: Optional[str] = None


class VariantUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    weight: Optional[str] = None
    purchase_price: Optional[Decimal] = None
    sale_price: Optional[Decimal] = None
    quantity: Optional[int] = None
    barcode: Optional[str] = None
    is_active: Optional[bool] = None


class VariantResponse(VariantCreate):
    id: int
    product_id: int
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# SALE RETURN SCHEMAS (5.5)
# ============================================
class SaleReturnItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal
    reason: Optional[str] = None


class SaleReturnItemResponse(BaseModel):
    id: int
    return_id: int
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    quantity: int
    unit_price: Decimal
    total: Decimal
    reason: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SaleReturnCreate(BaseModel):
    sale_id: int
    reason: Optional[str] = None
    refund_method: str = "كاش"
    restock: bool = True
    notes: Optional[str] = None
    items: List[SaleReturnItemCreate]


class SaleReturnResponse(BaseModel):
    id: int
    return_no: str
    sale_id: Optional[int] = None
    sale_invoice_no: Optional[str] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    return_date: date
    subtotal: Decimal
    tax_amount: Decimal = Decimal("0")
    total: Decimal
    refund_method: str
    refund_amount: Decimal
    reason: Optional[str] = None
    status: str
    restock: bool
    notes: Optional[str] = None
    items: List[SaleReturnItemResponse] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# INSTALLMENT SCHEMAS (5.6)
# ============================================
class InstallmentCreate(BaseModel):
    sale_id: int
    num_installments: int = Field(..., ge=2, le=24)
    first_payment: Decimal = Decimal("0")


class InstallmentResponse(BaseModel):
    id: int
    sale_id: int
    customer_id: Optional[int] = None
    installment_no: int
    amount: Decimal
    due_date: date
    paid_date: Optional[date] = None
    paid_amount: Decimal = Decimal("0")
    status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InstallmentPayment(BaseModel):
    amount: Decimal = Field(..., gt=0)
    notes: Optional[str] = None


# ============================================
# SHIFT SCHEMAS (5.9-5.11)
# ============================================
class ShiftOpen(BaseModel):
    opening_balance: Decimal = Decimal("0")
    notes: Optional[str] = None


class ShiftClose(BaseModel):
    closing_balance: Decimal
    notes: Optional[str] = None


class ShiftResponse(BaseModel):
    id: int
    user_id: int
    username: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    opening_balance: Decimal
    closing_balance: Optional[Decimal] = None
    expected_balance: Optional[Decimal] = None
    variance: Optional[Decimal] = None
    total_sales: Decimal = Decimal("0")
    total_returns: Decimal = Decimal("0")
    total_cash_in: Decimal = Decimal("0")
    total_cash_out: Decimal = Decimal("0")
    sales_count: int = 0
    returns_count: int = 0
    status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CashDrawerLogCreate(BaseModel):
    action: str  # open, cash_in, cash_out
    amount: Decimal = Decimal("0")
    reason: Optional[str] = None
    notes: Optional[str] = None


class CashDrawerLogResponse(BaseModel):
    id: int
    shift_id: Optional[int] = None
    user_id: Optional[int] = None
    action: str
    amount: Decimal
    reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# BATCH / EXPIRY SCHEMAS (5.14)
# ============================================
class BatchCreate(BaseModel):
    product_id: int
    batch_no: str
    quantity: int = 0
    manufacture_date: Optional[date] = None
    expiry_date: Optional[date] = None
    purchase_id: Optional[int] = None
    notes: Optional[str] = None


class BatchResponse(BaseModel):
    id: int
    product_id: int
    batch_no: str
    quantity: int
    manufacture_date: Optional[date] = None
    expiry_date: Optional[date] = None
    purchase_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# STOCKTAKE SCHEMAS (5.15)
# ============================================
class StocktakeItemCreate(BaseModel):
    product_id: int
    counted_quantity: int


class StocktakeItemResponse(BaseModel):
    id: int
    stocktake_id: int
    product_id: int
    product_name: Optional[str] = None
    system_quantity: int
    counted_quantity: Optional[int] = None
    variance: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StocktakeCreate(BaseModel):
    notes: Optional[str] = None
    items: Optional[List[StocktakeItemCreate]] = None  # can add items later


class StocktakeResponse(BaseModel):
    id: int
    reference: str
    stocktake_date: date
    status: str
    notes: Optional[str] = None
    created_by: Optional[int] = None
    completed_at: Optional[datetime] = None
    items: List[StocktakeItemResponse] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# E-INVOICE SCHEMAS (5.3)
# ============================================
class EInvoiceSubmit(BaseModel):
    sale_id: int


class EInvoiceResponse(BaseModel):
    id: int
    sale_id: Optional[int] = None
    internal_id: str
    eta_uuid: Optional[str] = None
    eta_submission_id: Optional[str] = None
    status: str
    document_type: str
    total_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    qr_code_data: Optional[str] = None
    submitted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# REPORTING SCHEMAS (5.21–5.24)
# ============================================
class HourlySalesItem(BaseModel):
    hour: int
    sales_count: int
    total_amount: Decimal


class DeadStockItem(BaseModel):
    id: int
    code: str
    name: str
    quantity: int
    last_sale_date: Optional[date] = None
    days_without_sale: int


class ProductMarginItem(BaseModel):
    id: int
    code: str
    name: str
    category: Optional[str] = None
    purchase_price: Decimal
    sale_price: Decimal
    margin: Decimal
    margin_percent: Decimal
    total_sold: int
    total_revenue: Decimal
    total_profit: Decimal


class CashierPerformanceItem(BaseModel):
    user_id: int
    username: str
    full_name: str
    sales_count: int
    total_sales: Decimal
    average_sale: Decimal
    returns_count: int
    total_returns: Decimal
