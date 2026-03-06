"""
CRUD Operations for all entities
"""
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, and_, desc
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
import models
import schemas


# ============================================
# CATEGORY CRUD
# ============================================
def get_categories(db: Session, skip: int = 0, limit: int = 100) -> list[models.Category]:
    return db.query(models.Category).offset(skip).limit(limit).all()


def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.id == category_id).first()


def get_category_by_code(db: Session, code: str) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.code == code).first()


def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, category: schemas.CategoryUpdate) -> Optional[models.Category]:
    db_category = get_category(db, category_id)
    if db_category:
        update_data = category.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)
        db.commit()
        db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    db_category = get_category(db, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
        return True
    return False


# ============================================
# SUPPLIER CRUD
# ============================================
def get_suppliers(db: Session, skip: int = 0, limit: int = 100) -> list[models.Supplier]:
    return db.query(models.Supplier).offset(skip).limit(limit).all()


def get_supplier(db: Session, supplier_id: int) -> Optional[models.Supplier]:
    return db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()


def get_supplier_by_code(db: Session, code: str) -> Optional[models.Supplier]:
    return db.query(models.Supplier).filter(models.Supplier.code == code).first()


def create_supplier(db: Session, supplier: schemas.SupplierCreate) -> models.Supplier:
    db_supplier = models.Supplier(**supplier.model_dump())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


def update_supplier(db: Session, supplier_id: int, supplier: schemas.SupplierUpdate) -> Optional[models.Supplier]:
    db_supplier = get_supplier(db, supplier_id)
    if db_supplier:
        update_data = supplier.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_supplier, key, value)
        db.commit()
        db.refresh(db_supplier)
    return db_supplier


def delete_supplier(db: Session, supplier_id: int) -> bool:
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
def get_customers(db: Session, skip: int = 0, limit: int = 100) -> list[models.Customer]:
    return db.query(models.Customer).offset(skip).limit(limit).all()


def get_customer(db: Session, customer_id: int) -> Optional[models.Customer]:
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def get_customer_by_code(db: Session, code: str) -> Optional[models.Customer]:
    return db.query(models.Customer).filter(models.Customer.code == code).first()


def create_customer(db: Session, customer: schemas.CustomerCreate) -> models.Customer:
    db_customer = models.Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def update_customer(db: Session, customer_id: int, customer: schemas.CustomerUpdate) -> Optional[models.Customer]:
    db_customer = get_customer(db, customer_id)
    if db_customer:
        update_data = customer.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_customer, key, value)
        db.commit()
        db.refresh(db_customer)
    return db_customer


def delete_customer(db: Session, customer_id: int) -> bool:
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
def get_products(db: Session, skip: int = 0, limit: int = 100, category: str = None) -> list[models.Product]:
    query = db.query(models.Product)
    if category and category != 'all':
        query = query.join(models.Category).filter(models.Category.code == category)
    return query.offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_product_by_code(db: Session, code: str) -> Optional[models.Product]:
    return db.query(models.Product).filter(models.Product.code == code).first()


def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    # Force quantity to 0 - stock only comes from purchases
    product_data = product.model_dump()
    product_data['quantity'] = 0
    db_product = models.Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: schemas.ProductUpdate) -> Optional[models.Product]:
    db_product = get_product(db, product_id)
    if db_product:
        update_data = product.model_dump(exclude_unset=True)
        # Prevent quantity changes from product form - quantity only changes via purchases/sales
        if 'quantity' in update_data:
            del update_data['quantity']
        for key, value in update_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
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


def get_products_with_details(db: Session, skip: int = 0, limit: int = 100, category: str = None) -> list[dict]:
    """Get products with category and supplier names (eager loaded)."""
    query = db.query(models.Product).options(
        joinedload(models.Product.category),
        joinedload(models.Product.supplier),
    )
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
def get_sales(db: Session, skip: int = 0, limit: int = 100) -> list[models.Sale]:
    return (
        db.query(models.Sale)
        .options(
            selectinload(models.Sale.items).joinedload(models.SaleItem.product),
            joinedload(models.Sale.customer),
        )
        .order_by(models.Sale.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_sale(db: Session, sale_id: int) -> Optional[models.Sale]:
    return (
        db.query(models.Sale)
        .options(
            selectinload(models.Sale.items).joinedload(models.SaleItem.product),
            joinedload(models.Sale.customer),
        )
        .filter(models.Sale.id == sale_id)
        .first()
    )


def generate_invoice_no(db: Session) -> str:
    count = db.query(models.Sale).count()
    return f"INV{str(count + 1).zfill(3)}"


def create_sale(db: Session, sale: schemas.SaleCreate, user_id: int = None) -> models.Sale:
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
            raise ValueError(f"المنتج غير موجود: {item.product_id}")
        if product.quantity < item.quantity:
            raise ValueError(f"الكمية غير كافية في المخزون. المنتج: {product.name}. المتاح: {product.quantity}")
        
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
        payment_method=sale.payment_method if sale.paid > 0 else None,
        notes=sale.notes,
        created_by=user_id
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
    
    # Add cash to balance for paid amount
    if sale.paid > 0:
        from sqlalchemy import text
        try:
            # Get current cash balance
            balance_result = db.execute(text("""
                SELECT balance_after FROM cash_transactions 
                ORDER BY created_at DESC LIMIT 1
            """)).fetchone()
            balance_before = float(balance_result[0]) if balance_result else 0.0
            balance_after = balance_before + float(sale.paid)
            
            # Record cash transaction
            db.execute(text("""
                INSERT INTO cash_transactions 
                (transaction_type, amount, balance_before, balance_after, reference_type, reference_id, description, created_by, created_at)
                VALUES (:type, :amount, :balance_before, :balance_after, :ref_type, :ref_id, :description, :created_by, NOW())
            """), {
                "type": "sale",
                "amount": float(sale.paid),
                "balance_before": balance_before,
                "balance_after": balance_after,
                "ref_type": "sale",
                "ref_id": db_sale.id,
                "description": f"إيرادات من فاتورة بيع #{invoice_no}",
                "created_by": user_id
            })
        except Exception as e:
            # Table might not exist, continue without error
            pass
    
    db.commit()
    db.refresh(db_sale)
    return db_sale


def delete_sale(db: Session, sale_id: int) -> bool:
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


def update_sale(db: Session, sale_id: int, sale: schemas.SaleCreate, user_id: int = None) -> models.Sale:
    """Update an existing sale - reverses old inventory and applies new"""
    db_sale = get_sale(db, sale_id)
    if not db_sale:
        raise ValueError(f"Sale {sale_id} not found")
    
    # Step 1: Restore old inventory (reverse the original sale)
    old_customer = get_customer(db, db_sale.customer_id) if db_sale.customer_id else None
    for item in db_sale.items:
        if item.product_id:
            product = get_product(db, item.product_id)
            if product:
                quantity_before = product.quantity
                product.quantity += item.quantity
                movement = models.InventoryMovement(
                    product_id=product.id,
                    movement_type='sale_reversal',
                    quantity_before=quantity_before,
                    quantity_change=item.quantity,
                    quantity_after=product.quantity,
                    reason='sale_edited',
                    reference_type='sale',
                    reference_id=sale_id
                )
                db.add(movement)
    
    # Reverse old customer balance
    if old_customer:
        old_customer.total_purchases = max(Decimal("0"), old_customer.total_purchases - db_sale.total)
        old_customer.balance = max(Decimal("0"), old_customer.balance - db_sale.remaining)
    
    # Delete old sale items
    for item in db_sale.items:
        db.delete(item)
    db.flush()
    
    # Step 2: Apply new sale data
    customer_name = sale.customer_name or "عميل نقدي"
    if sale.customer_id:
        customer = get_customer(db, sale.customer_id)
        if customer:
            customer_name = customer.name
    
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
    
    # Update sale record
    db_sale.customer_id = sale.customer_id
    db_sale.customer_name = customer_name
    db_sale.sale_date = sale.sale_date or date.today()
    db_sale.subtotal = subtotal
    db_sale.discount = sale.discount
    db_sale.total = total
    db_sale.paid = sale.paid
    db_sale.remaining = max(remaining, Decimal("0"))
    db_sale.status = status
    db_sale.payment_method = sale.payment_method if sale.paid > 0 else None
    db_sale.notes = sale.notes
    db_sale.updated_by = user_id
    db.flush()
    
    # Create new sale items and update inventory
    for item_data in sale_items:
        db_item = models.SaleItem(
            sale_id=db_sale.id,
            **item_data
        )
        db.add(db_item)
        
        product = get_product(db, item_data['product_id'])
        quantity_before = product.quantity
        product.quantity -= item_data['quantity']
        
        movement = models.InventoryMovement(
            product_id=product.id,
            movement_type='sale',
            quantity_before=quantity_before,
            quantity_change=-item_data['quantity'],
            quantity_after=product.quantity,
            reason='sale_edited',
            reference_type='sale',
            reference_id=db_sale.id
        )
        db.add(movement)
    
    # Update new customer balance
    if sale.customer_id:
        new_customer = get_customer(db, sale.customer_id)
        if new_customer:
            new_customer.total_purchases += total
            new_customer.balance += max(remaining, Decimal("0"))
    
    db.commit()
    db.refresh(db_sale)
    return db_sale


# ============================================
# PURCHASE CRUD
# ============================================
def get_purchases(db: Session, skip: int = 0, limit: int = 100) -> list[models.Purchase]:
    return (
        db.query(models.Purchase)
        .options(
            selectinload(models.Purchase.items).joinedload(models.PurchaseItem.product),
            joinedload(models.Purchase.supplier),
        )
        .order_by(models.Purchase.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_purchase(db: Session, purchase_id: int) -> Optional[models.Purchase]:
    return (
        db.query(models.Purchase)
        .options(
            selectinload(models.Purchase.items).joinedload(models.PurchaseItem.product),
            joinedload(models.Purchase.supplier),
        )
        .filter(models.Purchase.id == purchase_id)
        .first()
    )


def generate_purchase_invoice_no(db: Session) -> str:
    count = db.query(models.Purchase).count()
    return f"PUR{str(count + 1).zfill(3)}"


def create_purchase(db: Session, purchase: schemas.PurchaseCreate, user_id: int = None) -> models.Purchase:
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
            raise ValueError(f"المنتج غير موجود: {item.product_id}")
        
        item_total = item.unit_price * item.quantity
        subtotal += item_total
        
        # Use the purchase's supplier for items, not the product's supplier
        purchase_items.append({
            'product_id': item.product_id,
            'product_name': product.name,
            'supplier_id': purchase.supplier_id,
            'supplier_name': supplier_name,
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
        payment_method=purchase.payment_method if purchase.paid > 0 else None,
        notes=purchase.notes,
        created_by=user_id
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
    
    # Deduct cash from balance for paid amount
    if purchase.paid > 0:
        from sqlalchemy import text
        try:
            # Get current cash balance
            balance_result = db.execute(text("""
                SELECT balance_after FROM cash_transactions 
                ORDER BY created_at DESC LIMIT 1
            """)).fetchone()
            balance_before = float(balance_result[0]) if balance_result else 0.0
            
            # Check sufficient funds
            if balance_before < float(purchase.paid):
                raise ValueError(f"الرصيد النقدي غير كافٍ. المتاح: {balance_before} ج.م، المطلوب: {purchase.paid} ج.م")
            
            balance_after = balance_before - float(purchase.paid)
            
            # Record cash transaction
            db.execute(text("""
                INSERT INTO cash_transactions 
                (transaction_type, amount, balance_before, balance_after, reference_type, reference_id, description, created_by, created_at)
                VALUES (:type, :amount, :balance_before, :balance_after, :ref_type, :ref_id, :description, :created_by, NOW())
            """), {
                "type": "purchase",
                "amount": float(purchase.paid),
                "balance_before": balance_before,
                "balance_after": balance_after,
                "ref_type": "purchase",
                "ref_id": db_purchase.id,
                "description": f"دفع لمورد - فاتورة شراء #{invoice_no}",
                "created_by": user_id
            })
        except ValueError:
            raise
        except Exception as e:
            # Table might not exist, continue without error
            pass
    
    db.commit()
    db.refresh(db_purchase)
    return db_purchase


def delete_purchase(db: Session, purchase_id: int) -> bool:
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


def update_purchase(db: Session, purchase_id: int, purchase: schemas.PurchaseCreate, user_id: int = None) -> models.Purchase:
    """Update an existing purchase - reverses old inventory and applies new"""
    db_purchase = get_purchase(db, purchase_id)
    if not db_purchase:
        raise ValueError(f"Purchase {purchase_id} not found")
    
    # Step 1: Validate that reversing won't cause negative stock
    for item in db_purchase.items:
        if item.product_id:
            product = get_product(db, item.product_id)
            if product and product.quantity < item.quantity:
                raise ValueError(f"Cannot edit: would result in negative stock for {product.name}")
    
    # Step 2: Reverse old inventory
    old_supplier = get_supplier(db, db_purchase.supplier_id) if db_purchase.supplier_id else None
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
                    reason='purchase_edited',
                    reference_type='purchase',
                    reference_id=purchase_id
                )
                db.add(movement)
    
    # Reverse old supplier balance
    if old_supplier:
        old_supplier.total_purchases = max(Decimal("0"), old_supplier.total_purchases - db_purchase.total)
        old_supplier.balance = max(Decimal("0"), old_supplier.balance - db_purchase.remaining)
    
    # Delete old purchase items
    for item in db_purchase.items:
        db.delete(item)
    db.flush()
    
    # Step 3: Apply new purchase data
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
        
        # Use the purchase's supplier for items, not the product's supplier
        purchase_items.append({
            'product_id': item.product_id,
            'product_name': product.name,
            'supplier_id': purchase.supplier_id,
            'supplier_name': supplier_name,
            'quantity': item.quantity,
            'unit_price': item.unit_price,
            'total': item_total
        })
    
    total = subtotal - purchase.discount
    remaining = total - purchase.paid
    status = "مدفوعة" if remaining <= 0 else ("جزئي" if purchase.paid > 0 else "غير مدفوعة")
    
    # Update purchase record
    db_purchase.supplier_id = purchase.supplier_id
    db_purchase.supplier_name = supplier_name
    db_purchase.purchase_date = purchase.purchase_date or date.today()
    db_purchase.subtotal = subtotal
    db_purchase.discount = purchase.discount
    db_purchase.total = total
    db_purchase.paid = purchase.paid
    db_purchase.remaining = max(remaining, Decimal("0"))
    db_purchase.status = status
    db_purchase.payment_method = purchase.payment_method if purchase.paid > 0 else None
    db_purchase.notes = purchase.notes
    db_purchase.updated_by = user_id
    db.flush()
    
    # Create new purchase items and update inventory
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
            reason='purchase_edited',
            reference_type='purchase',
            reference_id=db_purchase.id
        )
        db.add(movement)
    
    # Update new supplier balance
    if purchase.supplier_id:
        new_supplier = get_supplier(db, purchase.supplier_id)
        if new_supplier:
            new_supplier.total_purchases += total
            new_supplier.balance += max(remaining, Decimal("0"))
    
    db.commit()
    db.refresh(db_purchase)
    return db_purchase


# ============================================
# INVENTORY CRUD
# ============================================
def get_inventory_movements(db: Session, product_id: int = None, skip: int = 0, limit: int = 100) -> list[dict]:
    query = db.query(models.InventoryMovement).options(
        joinedload(models.InventoryMovement.product)
    )
    if product_id:
        query = query.filter(models.InventoryMovement.product_id == product_id)
    movements = query.order_by(models.InventoryMovement.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for movement in movements:
        movement_dict = {
            'id': movement.id,
            'product_id': movement.product_id,
            'product_name': movement.product.name if movement.product else None,
            'movement_type': movement.movement_type,
            'quantity_before': movement.quantity_before,
            'quantity_change': movement.quantity_change,
            'quantity_after': movement.quantity_after,
            'reason': movement.reason,
            'reference_type': movement.reference_type,
            'reference_id': movement.reference_id,
            'notes': movement.notes,
            'created_at': movement.created_at
        }
        result.append(movement_dict)
    return result


def adjust_inventory(db: Session, adjustment: schemas.InventoryAdjustment) -> models.InventoryMovement:
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
def get_settings(db: Session) -> list[models.Setting]:
    return db.query(models.Setting).all()


def get_setting(db: Session, key: str) -> Optional[models.Setting]:
    return db.query(models.Setting).filter(models.Setting.key == key).first()


def update_settings(db: Session, settings: List[schemas.SettingUpdate]) -> list[models.Setting]:
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
def get_dashboard_stats(db: Session) -> schemas.DashboardStats:
    total_sales = db.query(func.coalesce(func.sum(models.Sale.total), 0)).scalar()
    total_products = db.query(models.Product).count()
    total_customers = db.query(models.Customer).count()
    
    today = date.today()
    today_sales = (
        db.query(models.Sale)
        .options(selectinload(models.Sale.items).joinedload(models.SaleItem.product))
        .filter(models.Sale.sale_date == today)
        .all()
    )
    
    today_profit = Decimal("0")
    for sale in today_sales:
        for item in sale.items:
            if item.product:
                profit = (item.unit_price - item.product.purchase_price) * item.quantity
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


def get_low_stock_products(db: Session) -> list[schemas.LowStockProduct]:
    products = db.query(models.Product).options(
        joinedload(models.Product.category)
    ).filter(
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


def get_profit_report(db: Session, from_date: date = None, to_date: date = None) -> schemas.ProfitReport:
    query = db.query(models.Sale).options(
        selectinload(models.Sale.items).joinedload(models.SaleItem.product)
    )
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


# ============================================
# ANALYTICS FUNCTIONS
# ============================================
def get_sales_trend(db: Session, period: str = 'daily', days: int = 30) -> schemas.SalesTrendReport:
    """Get sales trend data for charting"""
    from datetime import timedelta
    
    today = date.today()
    start_date = today - timedelta(days=days)
    
    sales = (
        db.query(models.Sale)
        .options(selectinload(models.Sale.items).joinedload(models.SaleItem.product))
        .filter(models.Sale.sale_date >= start_date)
        .order_by(models.Sale.sale_date)
        .all()
    )
    
    # Group by date
    daily_data = {}
    for sale in sales:
        date_key = str(sale.sale_date)
        if date_key not in daily_data:
            daily_data[date_key] = {'sales': Decimal('0'), 'profit': Decimal('0'), 'orders': 0}
        
        daily_data[date_key]['sales'] += sale.total
        daily_data[date_key]['orders'] += 1
        
        # Calculate profit for this sale
        for item in sale.items:
            if item.product:
                profit = (item.unit_price - item.product.purchase_price) * item.quantity
                daily_data[date_key]['profit'] += profit
    
    # Fill missing dates
    result = []
    current = start_date
    while current <= today:
        date_key = str(current)
        if date_key in daily_data:
            result.append(schemas.SalesTrendItem(
                date=date_key,
                sales=daily_data[date_key]['sales'],
                profit=daily_data[date_key]['profit'],
                orders=daily_data[date_key]['orders']
            ))
        else:
            result.append(schemas.SalesTrendItem(
                date=date_key,
                sales=Decimal('0'),
                profit=Decimal('0'),
                orders=0
            ))
        current += timedelta(days=1)
    
    return schemas.SalesTrendReport(data=result, period=period)


def get_top_products(db: Session, limit: int = 10) -> list[schemas.TopProductItem]:
    """Get top selling products by revenue using a single aggregation query."""
    results = (
        db.query(
            models.SaleItem.product_id,
            models.Product.name,
            models.Product.purchase_price,
            func.sum(models.SaleItem.quantity).label('quantity_sold'),
            func.sum(models.SaleItem.total).label('revenue'),
        )
        .join(models.Product, models.SaleItem.product_id == models.Product.id)
        .group_by(models.SaleItem.product_id, models.Product.name, models.Product.purchase_price)
        .order_by(func.sum(models.SaleItem.total).desc())
        .limit(limit)
        .all()
    )
    
    return [
        schemas.TopProductItem(
            id=r.product_id,
            name=r.name,
            quantity_sold=r.quantity_sold,
            revenue=r.revenue,
            profit=r.revenue - (r.purchase_price * r.quantity_sold)
        )
        for r in results
    ]


def get_inventory_value(db: Session) -> schemas.InventoryValueReport:
    """Calculate total inventory value and stock health"""
    products = db.query(models.Product).all()
    
    total_items = len(products)
    total_quantity = 0
    total_cost_value = Decimal('0')
    total_sale_value = Decimal('0')
    
    good_stock = 0
    low_stock = 0
    out_of_stock = 0
    
    for p in products:
        total_quantity += p.quantity
        total_cost_value += p.purchase_price * p.quantity
        total_sale_value += p.sale_price * p.quantity
        
        if p.quantity == 0:
            out_of_stock += 1
        elif p.quantity <= p.min_quantity:
            low_stock += 1
        else:
            good_stock += 1
    
    return schemas.InventoryValueReport(
        total_items=total_items,
        total_quantity=total_quantity,
        total_cost_value=total_cost_value,
        total_sale_value=total_sale_value,
        potential_profit=total_sale_value - total_cost_value,
        stock_health={'good': good_stock, 'low': low_stock, 'out': out_of_stock}
    )


def get_business_kpis(db: Session) -> schemas.BusinessKPIs:
    """Calculate comprehensive business KPIs"""
    from datetime import timedelta
    
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_start = today.replace(day=1)
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)
    last_month_end = month_start - timedelta(days=1)
    
    # Get all sales with items and products eager-loaded
    all_sales = (
        db.query(models.Sale)
        .options(selectinload(models.Sale.items).joinedload(models.SaleItem.product))
        .all()
    )
    today_sales = [s for s in all_sales if s.sale_date == today]
    week_sales = [s for s in all_sales if s.sale_date >= week_ago]
    month_sales = [s for s in all_sales if s.sale_date >= month_start]
    last_month_sales = [s for s in all_sales if last_month_start <= s.sale_date <= last_month_end]
    
    # Revenue calculations
    total_revenue = sum(s.total for s in all_sales) if all_sales else Decimal('0')
    today_revenue = sum(s.total for s in today_sales) if today_sales else Decimal('0')
    week_revenue = sum(s.total for s in week_sales) if week_sales else Decimal('0')
    month_revenue = sum(s.total for s in month_sales) if month_sales else Decimal('0')
    last_month_revenue = sum(s.total for s in last_month_sales) if last_month_sales else Decimal('0')
    
    # Profit calculations
    total_cost = Decimal('0')
    total_discount = Decimal('0')
    for sale in all_sales:
        total_discount += sale.discount
        for item in sale.items:
            if item.product:
                total_cost += item.product.purchase_price * item.quantity
    
    gross_profit = sum(s.subtotal for s in all_sales) - total_cost if all_sales else Decimal('0')
    net_profit = gross_profit - total_discount
    
    gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else Decimal('0')
    net_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else Decimal('0')
    
    # Average order value
    total_orders = len(all_sales)
    aov = total_revenue / total_orders if total_orders > 0 else Decimal('0')
    
    # Receivables and Payables
    pending_receivables = db.query(func.coalesce(func.sum(models.Customer.balance), 0)).scalar()
    pending_payables = db.query(func.coalesce(func.sum(models.Supplier.balance), 0)).scalar()
    
    # Inventory metrics
    inventory_data = get_inventory_value(db)
    
    # Growth calculations
    revenue_growth = ((month_revenue - last_month_revenue) / last_month_revenue * 100) if last_month_revenue > 0 else Decimal('0')
    last_month_orders = len(last_month_sales)
    orders_growth = ((len(month_sales) - last_month_orders) / last_month_orders * 100) if last_month_orders > 0 else Decimal('0')
    
    return schemas.BusinessKPIs(
        total_revenue=total_revenue,
        today_revenue=today_revenue,
        this_week_revenue=week_revenue,
        this_month_revenue=month_revenue,
        gross_profit_margin=round(gross_margin, 2),
        net_profit_margin=round(net_margin, 2),
        average_order_value=round(aov, 2),
        total_orders=total_orders,
        pending_receivables=pending_receivables,
        pending_payables=pending_payables,
        inventory_value=inventory_data.total_cost_value,
        inventory_items=inventory_data.total_items,
        low_stock_items=inventory_data.stock_health['low'],
        out_of_stock_items=inventory_data.stock_health['out'],
        revenue_growth=round(revenue_growth, 2),
        orders_growth=round(orders_growth, 2)
    )


def get_top_customers(db: Session, limit: int = 10) -> list[schemas.CustomerAnalyticsItem]:
    """Get top customers by purchase amount using a single aggregation query."""
    from sqlalchemy import case
    
    results = (
        db.query(
            models.Customer.id,
            models.Customer.name,
            models.Customer.total_purchases,
            models.Customer.balance,
            func.count(models.Sale.id).label('orders_count'),
            func.max(models.Sale.sale_date).label('last_purchase'),
        )
        .outerjoin(models.Sale, models.Customer.id == models.Sale.customer_id)
        .group_by(models.Customer.id, models.Customer.name, models.Customer.total_purchases, models.Customer.balance)
        .order_by(models.Customer.total_purchases.desc())
        .limit(limit)
        .all()
    )
    
    return [
        schemas.CustomerAnalyticsItem(
            id=r.id,
            name=r.name,
            total_purchases=r.total_purchases,
            orders_count=r.orders_count,
            balance=r.balance,
            last_purchase=r.last_purchase
        )
        for r in results
    ]

