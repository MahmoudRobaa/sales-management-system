"""
Mock Data Seed Script
Inserts sample categories, suppliers, customers, products, sales, and purchases
for testing and demonstration purposes.

Usage:
    python seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta
from decimal import Decimal
import random

from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

def seed():
    db: Session = SessionLocal()

    # Check if data already exists
    existing = db.query(models.Product).count()
    if existing > 0:
        print(f"يوجد بالفعل {existing} منتج في قاعدة البيانات.")
        ans = input("هل تريد إضافة بيانات تجريبية إضافية؟ (y/n): ").strip().lower()
        if ans != 'y':
            print("تم الإلغاء.")
            db.close()
            return

    print("جاري إدخال البيانات التجريبية...")

    # ── Categories ──
    categories_data = [
        ("CAT01", "Electronics", "إلكترونيات", "أجهزة ومعدات إلكترونية"),
        ("CAT02", "Electrical", "كهربائيات", "أدوات ومستلزمات كهربائية"),
        ("CAT03", "Accessories", "إكسسوارات", "إكسسوارات وملحقات"),
        ("CAT04", "Cables", "كابلات وأسلاك", "كابلات وتوصيلات"),
        ("CAT05", "Tools", "أدوات", "عدد وأدوات يدوية"),
        ("CAT06", "Lighting", "إضاءة", "مصابيح ولمبات"),
        ("CAT07", "Storage", "تخزين", "وسائط تخزين"),
    ]
    categories = []
    for code, name, name_ar, desc in categories_data:
        existing_cat = db.query(models.Category).filter(models.Category.code == code).first()
        if not existing_cat:
            cat = models.Category(code=code, name=name, name_ar=name_ar, description=desc)
            db.add(cat)
            db.flush()
            categories.append(cat)
        else:
            categories.append(existing_cat)
    print(f"  ✓ {len(categories)} فئة")

    # ── Suppliers ──
    suppliers_data = [
        ("SUP01", "شركة الفا للإلكترونيات", "01012345678", "القاهرة - شارع الجمهورية"),
        ("SUP02", "مؤسسة النور للكهرباء", "01123456789", "الإسكندرية - شارع النهضة"),
        ("SUP03", "شركة التقنية الحديثة", "01234567890", "القاهرة - مدينة نصر"),
        ("SUP04", "مصنع الأمل للكابلات", "01098765432", "المنصورة - المنطقة الصناعية"),
        ("SUP05", "وكالة السلام للاستيراد", "01187654321", "القاهرة - عين شمس"),
    ]
    suppliers = []
    for code, name, phone, address in suppliers_data:
        existing_sup = db.query(models.Supplier).filter(models.Supplier.code == code).first()
        if not existing_sup:
            sup = models.Supplier(code=code, name=name, phone=phone, address=address)
            db.add(sup)
            db.flush()
            suppliers.append(sup)
        else:
            suppliers.append(existing_sup)
    print(f"  ✓ {len(suppliers)} مورد")

    # ── Customers ──
    customers_data = [
        ("CUS01", "أحمد محمد", "01011111111", "القاهرة"),
        ("CUS02", "محل الإخوة للكهرباء", "01022222222", "الجيزة"),
        ("CUS03", "شركة البناء الحديث", "01033333333", "المعادي"),
        ("CUS04", "ورشة الأمان", "01044444444", "شبرا"),
        ("CUS05", "فني كهرباء - خالد", "01055555555", "مدينة نصر"),
        ("CUS06", "مؤسسة الصفا", "01066666666", "العباسية"),
        ("CUS07", "محلات النجاح", "01077777777", "الهرم"),
        ("CUS08", "مقاولات السلام", "01088888888", "حلوان"),
    ]
    customers = []
    for code, name, phone, address in customers_data:
        existing_cus = db.query(models.Customer).filter(models.Customer.code == code).first()
        if not existing_cus:
            cus = models.Customer(code=code, name=name, phone=phone, address=address, credit_limit=5000)
            db.add(cus)
            db.flush()
            customers.append(cus)
        else:
            customers.append(existing_cus)
    print(f"  ✓ {len(customers)} عميل")

    # ── Products ──
    products_data = [
        # (code, name, category_idx, supplier_idx, purchase_price, sale_price, quantity, min_qty, barcode)
        ("PRD001", "ماوس لاسلكي لوجيتك", 0, 0, 120, 175, 45, 10, "6901234567890"),
        ("PRD002", "كيبورد USB عادي", 0, 0, 80, 130, 60, 15, "6901234567891"),
        ("PRD003", "سماعة رأس ستيريو", 0, 0, 95, 160, 30, 8, "6901234567892"),
        ("PRD004", "شاحن هاتف سريع", 0, 2, 45, 85, 100, 20, "6901234567893"),
        ("PRD005", "كابل HDMI 2 متر", 3, 3, 25, 55, 80, 15, "6901234567894"),
        ("PRD006", "كابل USB Type-C", 3, 3, 18, 40, 120, 25, "6901234567895"),
        ("PRD007", "فلاشة USB 32GB", 6, 2, 50, 90, 70, 15, "6901234567896"),
        ("PRD008", "فلاشة USB 64GB", 6, 2, 75, 130, 50, 10, "6901234567897"),
        ("PRD009", "مفتاح كهرباء مفرد", 1, 1, 8, 18, 200, 50, "6902345678901"),
        ("PRD010", "مفتاح كهرباء مزدوج", 1, 1, 14, 28, 150, 40, "6902345678902"),
        ("PRD011", "بريزة ثلاثية", 1, 1, 20, 40, 100, 30, "6902345678903"),
        ("PRD012", "لمبة LED 9 وات", 5, 4, 12, 25, 300, 50, "6903456789012"),
        ("PRD013", "لمبة LED 15 وات", 5, 4, 18, 35, 250, 40, "6903456789013"),
        ("PRD014", "كشاف LED خارجي", 5, 4, 85, 150, 25, 5, "6903456789014"),
        ("PRD015", "سلك كهرباء 2.5مم (متر)", 3, 3, 5, 12, 500, 100, "6904567890123"),
        ("PRD016", "شريط عازل كهربائي", 4, 1, 4, 10, 200, 40, "6905678901234"),
        ("PRD017", "مفك مسطح كبير", 4, 4, 15, 30, 40, 10, "6905678901235"),
        ("PRD018", "مفك صليبة كبير", 4, 4, 15, 30, 35, 10, "6905678901236"),
        ("PRD019", "زرادية عادية 8 بوصة", 4, 4, 25, 50, 30, 8, "6905678901237"),
        ("PRD020", "قاطع كهرباء 16 أمبير", 1, 1, 22, 45, 60, 15, "6902345678904"),
        ("PRD021", "ترانس تنظيم 1000VA", 0, 0, 350, 550, 15, 3, "6901234567898"),
        ("PRD022", "UPS 600VA", 0, 0, 800, 1200, 10, 3, "6901234567899"),
        ("PRD023", "وصلة كهربائية 4 عين", 1, 1, 30, 60, 80, 20, "6902345678905"),
        ("PRD024", "جرس باب لاسلكي", 0, 2, 55, 100, 25, 5, "6901234567900"),
        ("PRD025", "كاميرا مراقبة WiFi", 0, 2, 250, 420, 12, 3, "6901234567901"),
        # Low-stock products (for testing reorder alerts)
        ("PRD026", "راوتر WiFi N300", 0, 2, 150, 280, 2, 5, "6901234567902"),
        ("PRD027", "سويتش شبكات 8 بورت", 0, 2, 120, 220, 1, 3, "6901234567903"),
        ("PRD028", "كابل شبكة Cat6 (متر)", 3, 3, 3, 8, 3, 20, "6904567890124"),
        ("PRD029", "لمبة ديكور LED", 5, 4, 35, 65, 0, 10, "6903456789015"),
        ("PRD030", "تايمر كهربائي رقمي", 1, 1, 45, 85, 1, 5, "6902345678906"),
    ]
    products = []
    for code, name, cat_idx, sup_idx, pp, sp, qty, min_q, barcode in products_data:
        existing_prod = db.query(models.Product).filter(models.Product.code == code).first()
        if not existing_prod:
            prod = models.Product(
                code=code, name=name,
                category_id=categories[cat_idx].id,
                supplier_id=suppliers[sup_idx].id,
                purchase_price=Decimal(str(pp)),
                sale_price=Decimal(str(sp)),
                quantity=qty, min_quantity=min_q,
                barcode=barcode,
                reorder_point=min_q,
            )
            db.add(prod)
            db.flush()
            products.append(prod)
        else:
            products.append(existing_prod)
    print(f"  ✓ {len(products)} منتج")

    # ── Sales (last 30 days) ──
    # Get admin user for created_by
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    user_id = admin.id if admin else 1

    sales_count = 0
    for day_offset in range(30, 0, -1):
        sale_date = date.today() - timedelta(days=day_offset)
        # 1-4 sales per day
        num_sales = random.randint(1, 4)
        for _ in range(num_sales):
            invoice_no = f"INV{db.query(models.Sale).count() + 1:05d}"
            # Check if invoice already exists
            if db.query(models.Sale).filter(models.Sale.invoice_no == invoice_no).first():
                continue

            customer = random.choice(customers) if random.random() > 0.3 else None
            payment_method = random.choice(["كاش", "كاش", "كاش", "فيزا", "تحويل بنكي"])

            # Pick 1-4 random products
            num_items = random.randint(1, 4)
            chosen_products = random.sample(products[:25], min(num_items, len(products[:25])))

            subtotal = Decimal("0")
            sale_items = []
            for p in chosen_products:
                qty = random.randint(1, 5)
                item_total = p.sale_price * qty
                subtotal += item_total
                sale_items.append((p, qty, item_total))

            discount = Decimal(str(random.choice([0, 0, 0, 5, 10, 20])))
            total = subtotal - discount
            paid = total  # fully paid

            sale = models.Sale(
                invoice_no=invoice_no,
                customer_id=customer.id if customer else None,
                customer_name=customer.name if customer else "عميل نقدي",
                sale_date=sale_date,
                subtotal=subtotal,
                discount=discount,
                tax_rate=Decimal("0"),
                tax_amount=Decimal("0"),
                total=total,
                paid=paid,
                remaining=Decimal("0"),
                status="completed",
                payment_method=payment_method,
                created_by=user_id,
            )
            db.add(sale)
            db.flush()

            for p, qty, item_total in sale_items:
                si = models.SaleItem(
                    sale_id=sale.id,
                    product_id=p.id,
                    product_name=p.name,
                    quantity=qty,
                    unit_price=p.sale_price,
                    tax_amount=Decimal("0"),
                    total=item_total,
                )
                db.add(si)

            sales_count += 1

    print(f"  ✓ {sales_count} فاتورة بيع")

    # ── Purchases (last 60 days) ──
    purchases_count = 0
    for day_offset in range(60, 0, -15):
        purchase_date = date.today() - timedelta(days=day_offset)
        for sup in suppliers:
            invoice_no = f"PUR{db.query(models.Purchase).count() + 1:05d}"
            if db.query(models.Purchase).filter(models.Purchase.invoice_no == invoice_no).first():
                continue

            sup_products = [p for p in products if p.supplier_id == sup.id]
            if not sup_products:
                continue

            chosen = random.sample(sup_products, min(random.randint(2, 5), len(sup_products)))
            subtotal = Decimal("0")
            pur_items = []
            for p in chosen:
                qty = random.randint(10, 50)
                item_total = p.purchase_price * qty
                subtotal += item_total
                pur_items.append((p, qty, item_total))

            total = subtotal
            purchase = models.Purchase(
                invoice_no=invoice_no,
                supplier_id=sup.id,
                supplier_name=sup.name,
                purchase_date=purchase_date,
                subtotal=subtotal,
                discount=Decimal("0"),
                total=total,
                paid=total,
                remaining=Decimal("0"),
                status="completed",
                payment_method="كاش",
                created_by=user_id,
            )
            db.add(purchase)
            db.flush()

            for p, qty, item_total in pur_items:
                pi = models.PurchaseItem(
                    purchase_id=purchase.id,
                    product_id=p.id,
                    product_name=p.name,
                    supplier_id=sup.id,
                    supplier_name=sup.name,
                    quantity=qty,
                    unit_price=p.purchase_price,
                    total=item_total,
                )
                db.add(pi)

            purchases_count += 1

    print(f"  ✓ {purchases_count} فاتورة شراء")

    db.commit()
    db.close()

    print("\n✅ تم إدخال البيانات التجريبية بنجاح!")
    print("   يمكنك الآن تصفح النظام ورؤية البيانات في جميع الأقسام")


if __name__ == "__main__":
    seed()
