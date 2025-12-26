"""
SQLAlchemy ORM Models
"""
from sqlalchemy import Column, Integer, String, Text, DECIMAL, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    name_ar = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    products = relationship("Product", back_populates="category")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
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

    id = Column(Integer, primary_key=True, index=True)
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

    sales = relationship("Sale", back_populates="customer")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"))
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"))
    purchase_price = Column(DECIMAL(15, 2), nullable=False, default=0)
    sale_price = Column(DECIMAL(15, 2), nullable=False, default=0)
    quantity = Column(Integer, nullable=False, default=0)
    min_quantity = Column(Integer, default=5)
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

    id = Column(Integer, primary_key=True, index=True)
    invoice_no = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"))
    customer_name = Column(String(200))
    sale_date = Column(Date, server_default=func.current_date())
    subtotal = Column(DECIMAL(15, 2), nullable=False, default=0)
    discount = Column(DECIMAL(15, 2), default=0)
    total = Column(DECIMAL(15, 2), nullable=False, default=0)
    paid = Column(DECIMAL(15, 2), default=0)
    remaining = Column(DECIMAL(15, 2), default=0)
    status = Column(String(50), default="pending")
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"))
    product_name = Column(String(200))
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(DECIMAL(15, 2), nullable=False)
    total = Column(DECIMAL(15, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
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
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    supplier = relationship("Supplier", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"))
    product_name = Column(String(200))
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(DECIMAL(15, 2), nullable=False)
    total = Column(DECIMAL(15, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product", back_populates="purchase_items")


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True, index=True)
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
