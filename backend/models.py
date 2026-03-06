"""
SQLAlchemy ORM Models
"""
from sqlalchemy import Column, Integer, String, Text, DECIMAL, Date, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=False)
    role = Column(String(50), nullable=False, default="cashier")  # admin, manager, cashier
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    activity_logs = relationship("ActivityLog", back_populates="user")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    username = Column(String(100))
    action = Column(String(100), nullable=False)  # create, update, delete, login, logout
    entity_type = Column(String(100))  # product, sale, purchase, etc.
    entity_id = Column(Integer)
    entity_name = Column(String(200))
    details = Column(Text)  # JSON with old/new values
    ip_address = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="activity_logs")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    payment_type = Column(String(50), nullable=False)  # sale, purchase
    reference_id = Column(Integer, nullable=False)  # sale_id or purchase_id
    amount = Column(DECIMAL(15, 2), nullable=False)
    payment_method = Column(String(50), default="كاش")
    payment_date = Column(Date, server_default=func.current_date())
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    name_ar = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    products = relationship("Product", back_populates="category")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    total_purchases = Column(DECIMAL(15, 2), default=0)
    balance = Column(DECIMAL(15, 2), default=0)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    products = relationship("Product", back_populates="supplier")
    purchases = relationship("Purchase", back_populates="supplier")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    total_purchases = Column(DECIMAL(15, 2), default=0)
    balance = Column(DECIMAL(15, 2), default=0)
    credit_limit = Column(DECIMAL(15, 2), default=0)
    loyalty_points = Column(Integer, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    sales = relationship("Sale", back_populates="customer")


class CashTransaction(Base):
    __tablename__ = "cash_transactions"

    id = Column(Integer, primary_key=True)
    transaction_type = Column(String(50), nullable=False)  # DEPOSIT, WITHDRAW, SALE, PURCHASE
    amount = Column(DECIMAL(15, 2), nullable=False)
    balance_before = Column(DECIMAL(15, 2), nullable=False, default=0)
    balance_after = Column(DECIMAL(15, 2), nullable=False, default=0)
    description = Column(Text)
    reference_type = Column(String(50))  # sale, purchase, manual
    reference_id = Column(Integer)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())

    creator = relationship("User")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"))
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"))
    purchase_price = Column(DECIMAL(15, 2), nullable=False, default=0)
    sale_price = Column(DECIMAL(15, 2), nullable=False, default=0)
    quantity = Column(Integer, default=0)
    min_quantity = Column(Integer, default=5)
    unit = Column(String(50), default="قطعة")
    barcode = Column(String(100))
    is_active = Column(Boolean, default=True)
    has_variants = Column(Boolean, default=False)
    reorder_point = Column(Integer, default=0)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")
    purchase_items = relationship("PurchaseItem", back_populates="product")
    inventory_movements = relationship("InventoryMovement", back_populates="product")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    invoice_no = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"))
    customer_name = Column(String(200))
    sale_date = Column(Date, server_default=func.current_date())
    subtotal = Column(DECIMAL(15, 2), nullable=False, default=0)
    discount = Column(DECIMAL(15, 2), default=0)
    tax_rate = Column(DECIMAL(5, 2), default=0)
    tax_amount = Column(DECIMAL(15, 2), default=0)
    total = Column(DECIMAL(15, 2), nullable=False, default=0)
    paid = Column(DECIMAL(15, 2), default=0)
    remaining = Column(DECIMAL(15, 2), default=0)
    status = Column(String(50), default="pending")
    payment_method = Column(String(50), default="كاش")
    is_held = Column(Boolean, default=False)
    held_name = Column(String(200))
    shift_id = Column(Integer, ForeignKey("shifts.id", ondelete="SET NULL"))
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    payments = relationship("SalePayment", back_populates="sale", cascade="all, delete-orphan")
    shift = relationship("Shift", back_populates="sales")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"))
    product_name = Column(String(200))
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="SET NULL"))
    variant_label = Column(String(200))
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(DECIMAL(15, 2), nullable=False)
    tax_amount = Column(DECIMAL(15, 2), default=0)
    total = Column(DECIMAL(15, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")
    variant = relationship("ProductVariant")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True)
    invoice_no = Column(String(50), unique=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"))
    supplier_name = Column(String(200))
    purchase_date = Column(Date, server_default=func.current_date())
    subtotal = Column(DECIMAL(15, 2), nullable=False, default=0)
    discount = Column(DECIMAL(15, 2), default=0)
    total = Column(DECIMAL(15, 2), nullable=False, default=0)
    paid = Column(DECIMAL(15, 2), default=0)
    remaining = Column(DECIMAL(15, 2), default=0)
    status = Column(String(50), default="pending")
    payment_method = Column(String(50), default="كاش")
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    supplier = relationship("Supplier", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"))
    product_name = Column(String(200))
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"))
    supplier_name = Column(String(200))
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(DECIMAL(15, 2), nullable=False)
    total = Column(DECIMAL(15, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product", back_populates="purchase_items")
    supplier = relationship("Supplier")


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    movement_type = Column(String(50), nullable=False)
    quantity_before = Column(Integer, nullable=False)
    quantity_change = Column(Integer, nullable=False)
    quantity_after = Column(Integer, nullable=False)
    reason = Column(String(100))
    reference_type = Column(String(50))
    reference_id = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="inventory_movements")


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text)
    description = Column(Text)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ============================================
# PRODUCT VARIANTS (5.12)
# ============================================
class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    sku = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)  # e.g. "Red / XL"
    size = Column(String(50))
    color = Column(String(50))
    weight = Column(String(50))
    purchase_price = Column(DECIMAL(15, 2), nullable=False, default=0)
    sale_price = Column(DECIMAL(15, 2), nullable=False, default=0)
    quantity = Column(Integer, default=0)
    barcode = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    product = relationship("Product", backref="variants")


# ============================================
# SPLIT PAYMENT (5.7)
# ============================================
class SalePayment(Base):
    __tablename__ = "sale_payments"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    payment_method = Column(String(50), nullable=False)  # cash, card, wallet
    amount = Column(DECIMAL(15, 2), nullable=False)
    reference_no = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    sale = relationship("Sale", back_populates="payments")


# ============================================
# SALES RETURNS / REFUNDS (5.5)
# ============================================
class SaleReturn(Base):
    __tablename__ = "sale_returns"

    id = Column(Integer, primary_key=True)
    return_no = Column(String(50), unique=True, nullable=False)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="SET NULL"))
    sale_invoice_no = Column(String(50))
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"))
    customer_name = Column(String(200))
    return_date = Column(Date, server_default=func.current_date())
    subtotal = Column(DECIMAL(15, 2), nullable=False, default=0)
    tax_amount = Column(DECIMAL(15, 2), default=0)
    total = Column(DECIMAL(15, 2), nullable=False, default=0)
    refund_method = Column(String(50), default="كاش")  # cash, credit, exchange
    refund_amount = Column(DECIMAL(15, 2), default=0)
    reason = Column(Text)
    status = Column(String(50), default="pending")  # pending, approved, completed
    restock = Column(Boolean, default=True)
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    sale = relationship("Sale")
    customer = relationship("Customer")
    items = relationship("SaleReturnItem", back_populates="sale_return", cascade="all, delete-orphan")


class SaleReturnItem(Base):
    __tablename__ = "sale_return_items"

    id = Column(Integer, primary_key=True)
    return_id = Column(Integer, ForeignKey("sale_returns.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"))
    product_name = Column(String(200))
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(DECIMAL(15, 2), nullable=False)
    total = Column(DECIMAL(15, 2), nullable=False)
    reason = Column(String(200))
    created_at = Column(DateTime, server_default=func.now())

    sale_return = relationship("SaleReturn", back_populates="items")
    product = relationship("Product")


# ============================================
# INSTALLMENT / CREDIT SALES (5.6)
# ============================================
class Installment(Base):
    __tablename__ = "installments"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"))
    installment_no = Column(Integer, nullable=False)
    amount = Column(DECIMAL(15, 2), nullable=False)
    due_date = Column(Date, nullable=False)
    paid_date = Column(Date)
    paid_amount = Column(DECIMAL(15, 2), default=0)
    status = Column(String(50), default="pending")  # pending, paid, overdue
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    sale = relationship("Sale")
    customer = relationship("Customer")


# ============================================
# SHIFT MANAGEMENT (5.9-5.11)
# ============================================
class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    username = Column(String(100))
    start_time = Column(DateTime, nullable=False, server_default=func.now())
    end_time = Column(DateTime)
    opening_balance = Column(DECIMAL(15, 2), nullable=False, default=0)
    closing_balance = Column(DECIMAL(15, 2))
    expected_balance = Column(DECIMAL(15, 2))
    variance = Column(DECIMAL(15, 2))
    total_sales = Column(DECIMAL(15, 2), default=0)
    total_returns = Column(DECIMAL(15, 2), default=0)
    total_cash_in = Column(DECIMAL(15, 2), default=0)
    total_cash_out = Column(DECIMAL(15, 2), default=0)
    sales_count = Column(Integer, default=0)
    returns_count = Column(Integer, default=0)
    status = Column(String(50), default="open")  # open, closed
    notes = Column(Text)
    closed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", foreign_keys=[user_id])
    closer = relationship("User", foreign_keys=[closed_by])
    sales = relationship("Sale", back_populates="shift")
    drawer_logs = relationship("CashDrawerLog", back_populates="shift")


class CashDrawerLog(Base):
    __tablename__ = "cash_drawer_logs"

    id = Column(Integer, primary_key=True)
    shift_id = Column(Integer, ForeignKey("shifts.id", ondelete="SET NULL"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(50), nullable=False)  # open, close, cash_in, cash_out
    amount = Column(DECIMAL(15, 2), default=0)
    reason = Column(String(200))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    shift = relationship("Shift", back_populates="drawer_logs")
    user = relationship("User")


# ============================================
# BATCH / EXPIRY TRACKING (5.14)
# ============================================
class ProductBatch(Base):
    __tablename__ = "product_batches"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    batch_no = Column(String(100), nullable=False)
    quantity = Column(Integer, default=0)
    manufacture_date = Column(Date)
    expiry_date = Column(Date)
    purchase_id = Column(Integer, ForeignKey("purchases.id", ondelete="SET NULL"))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    product = relationship("Product", backref="batches")
    purchase = relationship("Purchase")


# ============================================
# STOCKTAKE (5.15)
# ============================================
class Stocktake(Base):
    __tablename__ = "stocktakes"

    id = Column(Integer, primary_key=True)
    reference = Column(String(50), unique=True, nullable=False)
    stocktake_date = Column(Date, server_default=func.current_date())
    status = Column(String(50), default="in_progress")  # in_progress, completed, cancelled
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    completed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    creator = relationship("User")
    items = relationship("StocktakeItem", back_populates="stocktake", cascade="all, delete-orphan")


class StocktakeItem(Base):
    __tablename__ = "stocktake_items"

    id = Column(Integer, primary_key=True)
    stocktake_id = Column(Integer, ForeignKey("stocktakes.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    system_quantity = Column(Integer, nullable=False)
    counted_quantity = Column(Integer)
    variance = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    stocktake = relationship("Stocktake", back_populates="items")
    product = relationship("Product")


# ============================================
# ETA E-INVOICE (5.3)
# ============================================
class EInvoice(Base):
    __tablename__ = "einvoices"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="SET NULL"))
    internal_id = Column(String(100), nullable=False)
    eta_uuid = Column(String(200))
    eta_submission_id = Column(String(200))
    status = Column(String(50), default="draft")  # draft, submitted, accepted, rejected
    document_type = Column(String(50), default="I")  # I=invoice, C=credit, D=debit
    total_amount = Column(DECIMAL(15, 2))
    tax_amount = Column(DECIMAL(15, 2))
    qr_code_data = Column(Text)
    submission_response = Column(Text)
    submitted_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    sale = relationship("Sale")
