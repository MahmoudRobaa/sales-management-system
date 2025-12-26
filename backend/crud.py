"""
CRUD Operations for all entities
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
import models
import schemas


# ============================================
# CATEGORY CRUD
# ============================================
def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()


def get_category(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()


def get_category_by_code(db: Session, code: str):
    return db.query(models.Category).filter(models.Category.code == code).first()


def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, category: schemas.CategoryUpdate):
    db_category = get_category(db, category_id)
    if db_category:
        update_data = category.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)
        db.commit()
        db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int):
    db_category = get_category(db, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
        return True
    return False


# ============================================
# SUPPLIER CRUD
# ============================================
def get_suppliers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Supplier).offset(skip).limit(limit).all()


def get_supplier(db: Session, supplier_id: int):
    return db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()


def get_supplier_by_code(db: Session, code: str):
    return db.query(models.Supplier).filter(models.Supplier.code == code).first()


def create_supplier(db: Session, supplier: schemas.SupplierCreate):
    db_supplier = models.Supplier(**supplier.model_dump())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


def update_supplier(db: Session, supplier_id: int, supplier: schemas.SupplierUpdate):
    db_supplier = get_supplier(db, supplier_id)
    if db_supplier:
        update_data = supplier.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_supplier, key, value)
        db.commit()
        db.refresh(db_supplier)
    return db_supplier


def delete_supplier(db: Session, supplier_id: int):
    db_supplier = get_supplier(db, supplier_id)
    if db_supplier:
        db.delete(db_supplier)
        db.commit()
        return True
    return False


def generate_supplier_code(db: Session) -> str:
    """Generate unique supplier code based on max ID to avoid duplicates"""
    max_id = db.query(func.max(models.Supplier.id)).scalar() or 0
    return f"SUPP{str(max_id + 1).zfill(3)}"


# ============================================
# CUSTOMER CRUD
# ============================================
def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Customer).offset(skip).limit(limit).all()


def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def get_customer_by_code(db: Session, code: str):
    return db.query(models.Customer).filter(models.Customer.code == code).first()


def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_customer = models.Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def update_customer(db: Session, customer_id: int, customer: schemas.CustomerUpdate):
    db_customer = get_customer(db, customer_id)
    if db_customer:
        update_data = customer.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_customer, key, value)
        db.commit()
        db.refresh(db_customer)
    return db_customer


def delete_customer(db: Session, customer_id: int):
    db_customer = get_customer(db, customer_id)
    if db_customer:
        db.delete(db_customer)
        db.commit()
        return True
    return False


def generate_customer_code(db: Session) -> str:
    """Generate unique customer code based on max ID to avoid duplicates"""
    max_id = db.query(func.max(models.Customer.id)).scalar() or 0
    return f"CUST{str(max_id + 1).zfill(3)}"


# ============================================
# PRODUCT CRUD
# ============================================
def get_products(db: Session, skip: int = 0, limit: int = 100, category: str = None):
    query = db.query(models.Product)
    if category and category != 'all':
        query = query.join(models.Category).filter(models.Category.code == category)
    return query.offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_product_by_code(db: Session, code: str):
    return db.query(models.Product).filter(models.Product.code == code).first()


def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: schemas.ProductUpdate):
    db_product = get_product(db, product_id)
    if db_product:
        update_data = product.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False


def generate_product_code(db: Session) -> str:
    """Generate unique product code based on max ID to avoid duplicates"""
    max_id = db.query(func.max(models.Product.id)).scalar() or 0
    return f"PROD{str(max_id + 1).zfill(3)}"


def get_products_with_details(db: Session, skip: int = 0, limit: int = 100, category: str = None):
    """Get products with category and supplier names"""
    query = db.query(models.Product)
    if category and category != 'all':
        query = query.join(models.Category).filter(models.Category.code == category)
    
    products = query.offset(skip).limit(limit).all()
    result = []
    for p in products:
        product_dict = {
            'id': p.id,
            'code': p.code,
            'name': p.name,
            'category_id': p.category_id,
            'supplier_id': p.supplier_id,
            'purchase_price': p.purchase_price,
            'sale_price': p.sale_price,
            'quantity': p.quantity,
            'min_quantity': p.min_quantity,
            'description': p.description,
            'category': p.category.name_ar if p.category else None,
            'supplier': p.supplier.name if p.supplier else None
        }
        result.append(product_dict)
    return result


# ============================================
# SALE CRUD
# ============================================
def get_sales(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Sale).order_by(models.Sale.sale_date.desc()).offset(skip).limit(limit).all()


def get_sale(db: Session, sale_id: int):
    return db.query(models.Sale).filter(models.Sale.id == sale_id).first()


def generate_invoice_no(db: Session) -> str:
    count = db.query(models.Sale).count()
    return f"INV{str(count + 1).zfill(3)}"


def create_sale(db: Session, sale: schemas.SaleCreate):
    # Generate invoice number
    invoice_no = generate_invoice_no(db)
    
    # Get customer name
    customer_name = sale.customer_name or "عميل نقدي"
    if sale.customer_id:
        customer = get_customer(db, sale.customer_id)
        if customer:
            customer_name = customer.name
    
    # Calculate totals
    subtotal = Decimal("0")
    sale_items = []
    
    for item in sale.items:
        product = get_product(db, item.product_id)
        if not product:
            raise ValueError(f"Product {item.product_id} not found")
        if product.quantity < item.quantity:
            raise ValueError(f"Insufficient stock for {product.name}. Available: {product.quantity}")
        
        unit_price = item.unit_price if item.unit_price else product.sale_price
        item_total = unit_price * item.quantity
        subtotal += item_total
        
        sale_items.append({
            'product_id': item.product_id,
            'product_name': product.name,
            'quantity': item.quantity,
            'unit_price': unit_price,
            'total': item_total
        })
    
    total = subtotal - sale.discount
    remaining = total - sale.paid
    status = "مدفوعة" if remaining <= 0 else ("جزئي" if sale.paid > 0 else "غير مدفوعة")
    
    # Create sale
    db_sale = models.Sale(
        invoice_no=invoice_no,
        customer_id=sale.customer_id,
        customer_name=customer_name,
        sale_date=sale.sale_date or date.today(),
        subtotal=subtotal,
        discount=sale.discount,
        total=total,
        paid=sale.paid,
        remaining=max(remaining, Decimal("0")),
        status=status,
        notes=sale.notes
    )
    db.add(db_sale)
    db.flush()
    
    # Create sale items and update inventory
    for item_data in sale_items:
        db_item = models.SaleItem(
            sale_id=db_sale.id,
            **item_data
        )
        db.add(db_item)
        
        # Update product quantity
        product = get_product(db, item_data['product_id'])
        quantity_before = product.quantity
        product.quantity -= item_data['quantity']
        
        # Record inventory movement
        movement = models.InventoryMovement(
            product_id=product.id,
            movement_type='sale',
            quantity_before=quantity_before,
            quantity_change=-item_data['quantity'],
            quantity_after=product.quantity,
            reason='sale',
            reference_type='sale',
            reference_id=db_sale.id
        )
        db.add(movement)
    
    # Update customer balance if applicable
    if sale.customer_id:
        customer = get_customer(db, sale.customer_id)
        if customer:
            customer.total_purchases += total
            customer.balance += max(remaining, Decimal("0"))
    
    db.commit()
    db.refresh(db_sale)
    return db_sale


def delete_sale(db: Session, sale_id: int):
    db_sale = get_sale(db, sale_id)
    if db_sale:
        # Restore product quantities
        for item in db_sale.items:
            if item.product_id:
                product = get_product(db, item.product_id)
                if product:
                    quantity_before = product.quantity
                    product.quantity += item.quantity
                    
                    # Record inventory movement
                    movement = models.InventoryMovement(
                        product_id=product.id,
                        movement_type='sale_reversal',
                        quantity_before=quantity_before,
                        quantity_change=item.quantity,
                        quantity_after=product.quantity,
                        reason='sale_deleted',
                        reference_type='sale',
                        reference_id=sale_id
                    )
                    db.add(movement)
        
        # Update customer balance (prevent negative values)
        if db_sale.customer_id:
            customer = get_customer(db, db_sale.customer_id)
            if customer:
                customer.total_purchases = max(Decimal("0"), customer.total_purchases - db_sale.total)
                customer.balance = max(Decimal("0"), customer.balance - db_sale.remaining)
        
        db.delete(db_sale)
        db.commit()
        return True
    return False


# ============================================
# PURCHASE CRUD
# ============================================
def get_purchases(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Purchase).order_by(models.Purchase.purchase_date.desc()).offset(skip).limit(limit).all()


def get_purchase(db: Session, purchase_id: int):
    return db.query(models.Purchase).filter(models.Purchase.id == purchase_id).first()


def generate_purchase_invoice_no(db: Session) -> str:
    count = db.query(models.Purchase).count()
    return f"PUR{str(count + 1).zfill(3)}"


def create_purchase(db: Session, purchase: schemas.PurchaseCreate):
    invoice_no = generate_purchase_invoice_no(db)
    
    supplier_name = purchase.supplier_name
    if purchase.supplier_id:
        supplier = get_supplier(db, purchase.supplier_id)
        if supplier:
            supplier_name = supplier.name
    
    subtotal = Decimal("0")
    purchase_items = []
    
    for item in purchase.items:
        product = get_product(db, item.product_id)
        if not product:
            raise ValueError(f"Product {item.product_id} not found")
        
        item_total = item.unit_price * item.quantity
        subtotal += item_total
        
        purchase_items.append({
            'product_id': item.product_id,
            'product_name': product.name,
            'quantity': item.quantity,
            'unit_price': item.unit_price,
            'total': item_total
        })
    
    total = subtotal - purchase.discount
    remaining = total - purchase.paid
    status = "مدفوعة" if remaining <= 0 else ("جزئي" if purchase.paid > 0 else "غير مدفوعة")
    
    db_purchase = models.Purchase(
        invoice_no=invoice_no,
        supplier_id=purchase.supplier_id,
        supplier_name=supplier_name,
        purchase_date=purchase.purchase_date or date.today(),
        subtotal=subtotal,
        discount=purchase.discount,
        total=total,
        paid=purchase.paid,
        remaining=max(remaining, Decimal("0")),
        status=status,
        notes=purchase.notes
    )
    db.add(db_purchase)
    db.flush()
    
    for item_data in purchase_items:
        db_item = models.PurchaseItem(
            purchase_id=db_purchase.id,
            **item_data
        )
        db.add(db_item)
        
        product = get_product(db, item_data['product_id'])
        quantity_before = product.quantity
        product.quantity += item_data['quantity']
        
        movement = models.InventoryMovement(
            product_id=product.id,
            movement_type='purchase',
            quantity_before=quantity_before,
            quantity_change=item_data['quantity'],
            quantity_after=product.quantity,
            reason='purchase',
            reference_type='purchase',
            reference_id=db_purchase.id
        )
        db.add(movement)
    
    if purchase.supplier_id:
        supplier = get_supplier(db, purchase.supplier_id)
        if supplier:
            supplier.total_purchases += total
            supplier.balance += max(remaining, Decimal("0"))
    
    db.commit()
    db.refresh(db_purchase)
    return db_purchase


def delete_purchase(db: Session, purchase_id: int):
    db_purchase = get_purchase(db, purchase_id)
    if db_purchase:
        # Validate stock before deleting
        for item in db_purchase.items:
            if item.product_id:
                product = get_product(db, item.product_id)
                if product and product.quantity < item.quantity:
                    raise ValueError(f"Cannot delete purchase: would result in negative stock for {product.name}")
        
        for item in db_purchase.items:
            if item.product_id:
                product = get_product(db, item.product_id)
                if product:
                    quantity_before = product.quantity
                    product.quantity -= item.quantity
                    
                    movement = models.InventoryMovement(
                        product_id=product.id,
                        movement_type='purchase_reversal',
                        quantity_before=quantity_before,
                        quantity_change=-item.quantity,
                        quantity_after=product.quantity,
                        reason='purchase_deleted',
                        reference_type='purchase',
                        reference_id=purchase_id
                    )
                    db.add(movement)
        
        # Update supplier balance (prevent negative values)
        if db_purchase.supplier_id:
            supplier = get_supplier(db, db_purchase.supplier_id)
            if supplier:
                supplier.total_purchases = max(Decimal("0"), supplier.total_purchases - db_purchase.total)
                supplier.balance = max(Decimal("0"), supplier.balance - db_purchase.remaining)
        
        db.delete(db_purchase)
        db.commit()
        return True
    return False


# ============================================
# INVENTORY CRUD
# ============================================
def get_inventory_movements(db: Session, product_id: int = None, skip: int = 0, limit: int = 100):
    query = db.query(models.InventoryMovement)
    if product_id:
        query = query.filter(models.InventoryMovement.product_id == product_id)
    return query.order_by(models.InventoryMovement.created_at.desc()).offset(skip).limit(limit).all()


def adjust_inventory(db: Session, adjustment: schemas.InventoryAdjustment):
    product = get_product(db, adjustment.product_id)
    if not product:
        raise ValueError(f"Product {adjustment.product_id} not found")
    
    quantity_before = product.quantity
    
    if adjustment.adjustment_type == 'add':
        product.quantity += adjustment.quantity
    elif adjustment.adjustment_type == 'subtract':
        if product.quantity < adjustment.quantity:
            raise ValueError(f"Cannot subtract {adjustment.quantity}. Only {product.quantity} available.")
        product.quantity -= adjustment.quantity
    elif adjustment.adjustment_type == 'set':
        product.quantity = adjustment.quantity
    else:
        raise ValueError(f"Invalid adjustment type: {adjustment.adjustment_type}")
    
    quantity_change = product.quantity - quantity_before
    
    movement = models.InventoryMovement(
        product_id=product.id,
        movement_type=adjustment.adjustment_type,
        quantity_before=quantity_before,
        quantity_change=quantity_change,
        quantity_after=product.quantity,
        reason=adjustment.reason,
        reference_type='adjustment',
        notes=adjustment.notes
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


# ============================================
# SETTINGS CRUD
# ============================================
def get_settings(db: Session):
    return db.query(models.Setting).all()


def get_setting(db: Session, key: str):
    return db.query(models.Setting).filter(models.Setting.key == key).first()


def update_settings(db: Session, settings: List[schemas.SettingUpdate]):
    for setting in settings:
        db_setting = get_setting(db, setting.key)
        if db_setting:
            db_setting.value = setting.value
        else:
            db_setting = models.Setting(key=setting.key, value=setting.value)
            db.add(db_setting)
    db.commit()
    return get_settings(db)


# ============================================
# DASHBOARD & REPORTS
# ============================================
def get_dashboard_stats(db: Session):
    total_sales = db.query(func.coalesce(func.sum(models.Sale.total), 0)).scalar()
    total_products = db.query(models.Product).count()
    total_customers = db.query(models.Customer).count()
    
    today = date.today()
    today_sales = db.query(models.Sale).filter(models.Sale.sale_date == today).all()
    
    today_profit = Decimal("0")
    for sale in today_sales:
        for item in sale.items:
            if item.product_id:
                product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
                if product:
                    profit = (item.unit_price - product.purchase_price) * item.quantity
                    today_profit += profit
    
    min_stock_setting = db.query(models.Setting).filter(models.Setting.key == 'min_stock_alert').first()
    min_stock = int(min_stock_setting.value) if min_stock_setting and min_stock_setting.value else 5
    low_stock_count = db.query(models.Product).filter(
        models.Product.quantity <= models.Product.min_quantity
    ).count()
    
    return schemas.DashboardStats(
        total_sales=total_sales,
        total_products=total_products,
        total_customers=total_customers,
        today_profit=today_profit,
        low_stock_count=low_stock_count
    )


def get_low_stock_products(db: Session):
    products = db.query(models.Product).filter(
        models.Product.quantity <= models.Product.min_quantity
    ).all()
    
    result = []
    for p in products:
        if p.quantity == 0:
            status = "نفذ من المخزون"
        elif p.quantity <= (p.min_quantity / 2):
            status = "منخفض جدًا"
        else:
            status = "منخفض"
        
        result.append(schemas.LowStockProduct(
            id=p.id,
            name=p.name,
            category=p.category.name_ar if p.category else None,
            quantity=p.quantity,
            min_quantity=p.min_quantity,
            status=status
        ))
    return result


def get_profit_report(db: Session, from_date: date = None, to_date: date = None):
    query = db.query(models.Sale)
    if from_date:
        query = query.filter(models.Sale.sale_date >= from_date)
    if to_date:
        query = query.filter(models.Sale.sale_date <= to_date)
    
    sales = query.all()
    
    total_sales = Decimal("0")
    total_cost = Decimal("0")
    total_discount = Decimal("0")
    
    for sale in sales:
        total_sales += sale.subtotal
        total_discount += sale.discount
        
        for item in sale.items:
            if item.product_id:
                product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
                if product:
                    total_cost += product.purchase_price * item.quantity
    
    gross_profit = total_sales - total_cost
    net_profit = gross_profit - total_discount
    
    return schemas.ProfitReport(
        total_sales=total_sales,
        total_cost=total_cost,
        gross_profit=gross_profit,
        total_discount=total_discount,
        net_profit=net_profit,
        sales_count=len(sales)
    )
