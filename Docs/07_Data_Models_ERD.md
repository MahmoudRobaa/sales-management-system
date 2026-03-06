# Data Models & Entity Relationship Diagram
# نماذج البيانات ومخطط العلاقات

**Project:** Sales Management System  
**Version:** 2.0.0  
**Date:** March 2026  
**Database:** PostgreSQL 15

---

## 1. Entity Relationship Diagram (ERD)

```
                                    ┌─────────────────┐
                                    │     USERS       │
                                    ├─────────────────┤
                                    │ PK id           │
                                    │    username     │◄───────────────┐
                                    │    password_hash│                │
                                    │    full_name    │                │
                                    │    role         │                │
                                    │    is_active    │                │
                                    │    last_login   │                │
                                    │    created_at   │                │
                                    │    updated_at   │                │
                                    └────────┬────────┘                │
                                             │                         │
                                             │1                        │
                                             │                         │
                                             ▼*                        │
                                    ┌─────────────────┐                │
                                    │ ACTIVITY_LOGS   │                │
                                    ├─────────────────┤                │
                                    │ PK id           │                │
                                    │ FK user_id      │────────────────┘
                                    │    username     │
                                    │    action       │
                                    │    entity_type  │
                                    │    entity_id    │
                                    │    entity_name  │
                                    │    details      │
                                    │    ip_address   │
                                    │    created_at   │
                                    └─────────────────┘

┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   CATEGORIES    │         │    SUPPLIERS    │         │    CUSTOMERS    │
├─────────────────┤         ├─────────────────┤         ├─────────────────┤
│ PK id           │         │ PK id           │         │ PK id           │
│    code         │         │    code         │         │    code         │
│    name         │         │    name         │         │    name         │
│    name_ar      │         │    phone        │         │    phone        │
│    description  │         │    email        │         │    email        │
│    created_at   │         │    address      │         │    address      │
│    updated_at   │         │    total_purchases       │    total_purchases
└────────┬────────┘         │    balance      │         │    balance      │
         │                  │    notes        │         │    notes        │
         │1                 │    created_at   │         │    created_at   │
         │                  │    updated_at   │         │    updated_at   │
         │                  └────────┬────────┘         └────────┬────────┘
         │                           │                           │
         │   ┌───────────────────────┤                           │
         │   │1                      │1                          │1
         │   │                       │                           │
         ▼*  ▼*                      │                           │
┌─────────────────┐                  │                           │
│    PRODUCTS     │                  │                           │
├─────────────────┤                  │                           │
│ PK id           │                  │                           │
│    code         │                  │                           │
│    name         │                  │                           │
│ FK category_id  │──────────────────┘                           │
│ FK supplier_id  │◄─────────────────┐                           │
│    purchase_price                  │                           │
│    sale_price   │                  │                           │
│    quantity     │                  │                           │
│    min_quantity │                  │                           │
│    description  │                  │                           │
│    created_at   │                  │                           │
│    updated_at   │                  │                           │
└────────┬────────┘                  │                           │
         │                           │                           │
         │1                          │                           │
         ├─────────────────┬─────────┴─────────┐                 │
         │                 │                   │                 │
         │                 │                   │                 │
         ▼*                ▼*                  ▼*                ▼*
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   SALE_ITEMS    │  │ PURCHASE_ITEMS  │  │ INVENTORY_      │  │     SALES       │
├─────────────────┤  ├─────────────────┤  │   MOVEMENTS     │  ├─────────────────┤
│ PK id           │  │ PK id           │  ├─────────────────┤  │ PK id           │
│ FK sale_id      │  │ FK purchase_id  │  │ PK id           │  │    invoice_no   │
│ FK product_id   │  │ FK product_id   │  │ FK product_id   │  │ FK customer_id  │──┐
│    product_name │  │    product_name │  │    movement_type│  │    customer_name│  │
│    quantity     │  │ FK supplier_id  │  │    quantity_before   sale_date     │  │
│    unit_price   │  │    supplier_name│  │    quantity_change   subtotal      │  │
│    total        │  │    quantity     │  │    quantity_after    discount      │  │
│    created_at   │  │    unit_price   │  │    reason       │  │    total        │  │
└────────┬────────┘  │    total        │  │    reference_type    paid          │  │
         │           │    created_at   │  │    reference_id │  │    remaining    │  │
         │*          └────────┬────────┘  │    notes        │  │    status       │  │
         │                    │*          │    created_at   │  │    payment_method  │
         │                    │           └─────────────────┘  │    notes        │  │
         │                    │                                │ FK created_by   │  │
         │                    │                                │ FK updated_by   │  │
         │                    │                                │    created_at   │  │
         │                    │                                │    updated_at   │  │
         │                    │                                └────────┬────────┘  │
         │                    │                                         │1          │
         │                    │                                         ◄───────────┘
         │                    │                                         │
         │                    │                                         │
         │                    ▼1                                        │
         │           ┌─────────────────┐                               │
         │           │    PURCHASES    │                               │
         └──────────►├─────────────────┤                               │
                     │ PK id           │                               │
                     │    invoice_no   │                               │
                     │ FK supplier_id  │                               │
                     │    supplier_name│                               │
                     │    purchase_date│                               │
                     │    subtotal     │                               │
                     │    discount     │                               │
                     │    total        │                               │
                     │    paid         │                               │
                     │    remaining    │                               │
                     │    status       │                               │
                     │    payment_method                               │
                     │    notes        │                               │
                     │ FK created_by   │                               │
                     │ FK updated_by   │                               │
                     │    created_at   │                               │
                     │    updated_at   │                               │
                     └─────────────────┘                               │
                                                                       │
┌─────────────────┐         ┌─────────────────┐                       │
│    PAYMENTS     │         │ CASH_TRANSACTIONS                       │
├─────────────────┤         ├─────────────────┤                       │
│ PK id           │         │ PK id           │                       │
│    payment_type │         │    transaction_type                     │
│    reference_id │         │    amount       │                       │
│    amount       │         │    balance_before                       │
│    payment_method         │    balance_after│                       │
│    payment_date │         │    description  │                       │
│    notes        │         │    reference_type                       │
│ FK created_by   │         │    reference_id │                       │
│    created_at   │         │ FK created_by   │                       │
└─────────────────┘         │    created_at   │                       │
                            └─────────────────┘                       │
                                                                       │
┌─────────────────┐                                                   │
│    SETTINGS     │◄──────────────────────────────────────────────────┘
├─────────────────┤    (No direct FK, but referenced by app settings)
│ PK key          │
│    value        │
│    description  │
│    updated_at   │
└─────────────────┘
```

---

## 2. Table Definitions | تعريفات الجداول

### 2.1 Users Table (المستخدمين)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'cashier',  -- admin, manager, cashier
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:** `idx_users_username` on `username`

### 2.2 Activity Logs Table (سجل النشاط)

```sql
CREATE TABLE activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    username VARCHAR(100),
    action VARCHAR(100) NOT NULL,     -- create, update, delete, login, logout
    entity_type VARCHAR(100),          -- product, sale, purchase, etc.
    entity_id INTEGER,
    entity_name VARCHAR(200),
    details TEXT,                      -- JSON with old/new values
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:** `idx_activity_logs_user`, `idx_activity_logs_date`

### 2.3 Categories Table (الفئات)

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    name_ar VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.4 Suppliers Table (الموردين)

```sql
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    total_purchases DECIMAL(15, 2) DEFAULT 0,
    balance DECIMAL(15, 2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.5 Customers Table (العملاء)

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    total_purchases DECIMAL(15, 2) DEFAULT 0,
    balance DECIMAL(15, 2) DEFAULT 0,     -- Credit owed by customer
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.6 Products Table (المنتجات)

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
    description TEXT,
    purchase_price DECIMAL(15, 2) NOT NULL DEFAULT 0,
    sale_price DECIMAL(15, 2) NOT NULL DEFAULT 0,
    quantity INTEGER DEFAULT 0,
    min_quantity INTEGER DEFAULT 5,
    unit VARCHAR(50) DEFAULT 'قطعة',
    barcode VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:** `idx_products_category`, `idx_products_supplier`, `idx_products_code`

### 2.7 Sales Table (المبيعات)

```sql
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    invoice_no VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    customer_name VARCHAR(200),
    sale_date DATE DEFAULT CURRENT_DATE,
    subtotal DECIMAL(15, 2) NOT NULL DEFAULT 0,
    discount DECIMAL(15, 2) DEFAULT 0,
    total DECIMAL(15, 2) NOT NULL DEFAULT 0,
    paid DECIMAL(15, 2) DEFAULT 0,
    remaining DECIMAL(15, 2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'غير مدفوعة',  -- مدفوعة، جزئي، غير مدفوعة
    payment_method VARCHAR(50) DEFAULT 'كاش',
    notes TEXT,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:** `idx_sales_customer`, `idx_sales_date`, `idx_sales_invoice`

### 2.8 Sale Items Table (أصناف المبيعات)

```sql
CREATE TABLE sale_items (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
    product_name VARCHAR(200),
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(15, 2) NOT NULL,
    total DECIMAL(15, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:** `idx_sale_items_sale`, `idx_sale_items_product`

### 2.9 Purchases Table (المشتريات)

```sql
CREATE TABLE purchases (
    id SERIAL PRIMARY KEY,
    invoice_no VARCHAR(50) UNIQUE NOT NULL,
    supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
    supplier_name VARCHAR(200),
    purchase_date DATE DEFAULT CURRENT_DATE,
    subtotal DECIMAL(15, 2) NOT NULL DEFAULT 0,
    discount DECIMAL(15, 2) DEFAULT 0,
    total DECIMAL(15, 2) NOT NULL DEFAULT 0,
    paid DECIMAL(15, 2) DEFAULT 0,
    remaining DECIMAL(15, 2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'غير مدفوعة',
    payment_method VARCHAR(50) DEFAULT 'كاش',
    notes TEXT,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:** `idx_purchases_supplier`, `idx_purchases_date`

### 2.10 Purchase Items Table (أصناف المشتريات)

```sql
CREATE TABLE purchase_items (
    id SERIAL PRIMARY KEY,
    purchase_id INTEGER NOT NULL REFERENCES purchases(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
    product_name VARCHAR(200),
    supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
    supplier_name VARCHAR(200),
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(15, 2) NOT NULL,
    total DECIMAL(15, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:** `idx_purchase_items_purchase`, `idx_purchase_items_supplier`

### 2.11 Inventory Movements Table (حركات المخزون)

```sql
CREATE TABLE inventory_movements (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    movement_type VARCHAR(50) NOT NULL,  -- sale, purchase, adjustment_add, etc.
    quantity_before INTEGER NOT NULL,
    quantity_change INTEGER NOT NULL,
    quantity_after INTEGER NOT NULL,
    reason VARCHAR(100),
    reference_type VARCHAR(50),  -- sale, purchase, adjustment
    reference_id INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:** `idx_inventory_movements_product`, `idx_inventory_movements_date`

### 2.12 Cash Transactions Table (المعاملات المالية)

```sql
CREATE TABLE cash_transactions (
    id SERIAL PRIMARY KEY,
    transaction_type VARCHAR(50) NOT NULL,  -- deposit, withdraw, sale, purchase
    amount DECIMAL(15, 2) NOT NULL,
    balance_before DECIMAL(15, 2) NOT NULL DEFAULT 0,
    balance_after DECIMAL(15, 2) NOT NULL DEFAULT 0,
    description TEXT,
    reference_type VARCHAR(50),
    reference_id INTEGER,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:** `idx_cash_transactions_date`

### 2.13 Payments Table (المدفوعات)

```sql
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    payment_type VARCHAR(50) NOT NULL,  -- sale, purchase
    reference_id INTEGER NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'كاش',
    payment_date DATE DEFAULT CURRENT_DATE,
    notes TEXT,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.14 Settings Table (الإعدادات)

```sql
CREATE TABLE settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. Relationships Summary | ملخص العلاقات

| Parent | Child | Relationship | On Delete |
|--------|-------|--------------|-----------|
| Users | Activity Logs | 1:N | SET NULL |
| Users | Sales.created_by | 1:N | SET NULL |
| Users | Purchases.created_by | 1:N | SET NULL |
| Categories | Products | 1:N | SET NULL |
| Suppliers | Products | 1:N | SET NULL |
| Suppliers | Purchases | 1:N | SET NULL |
| Customers | Sales | 1:N | SET NULL |
| Products | Sale Items | 1:N | SET NULL |
| Products | Purchase Items | 1:N | SET NULL |
| Products | Inventory Movements | 1:N | CASCADE |
| Sales | Sale Items | 1:N | CASCADE |
| Purchases | Purchase Items | 1:N | CASCADE |

---

## 4. Data Types & Standards | أنواع البيانات والمعايير

### 4.1 Numeric Precision

| Type | Format | Usage |
|------|--------|-------|
| Money | DECIMAL(15, 2) | All monetary values (EGP) |
| Quantity | INTEGER | Product quantities |
| Percentage | DECIMAL(5, 2) | Tax rates, discounts |

### 4.2 Date/Time Standards

| Type | PostgreSQL | Python |
|------|------------|--------|
| Date only | DATE | date |
| Timestamp | TIMESTAMP | datetime |
| Default | CURRENT_TIMESTAMP | func.now() |

### 4.3 String Lengths

| Field Type | Max Length | Example |
|------------|------------|---------|
| Code | 50 | PROD001, CUST001 |
| Name | 200 | Product names, customer names |
| Username | 100 | admin, user1 |
| Email | 100 | user@domain.com |
| Phone | 20 | +20-123-456-7890 |
| Status | 50 | مدفوعة, جزئي |
| Text/Notes | TEXT (unlimited) | Long descriptions |

---

## 5. Default Data | البيانات الافتراضية

### 5.1 Default Admin User

```sql
INSERT INTO users (username, password_hash, full_name, role) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G3MDbpFpHHNdC.', 'مدير النظام', 'admin');
-- Password: admin123
```

### 5.2 Default Settings

```sql
INSERT INTO settings (key, value, description) VALUES
('store_name', 'محل الحاسوب والأدوات الكهربائية', 'اسم المتجر'),
('store_address', 'العنوان', 'عنوان المتجر'),
('store_phone', '', 'رقم هاتف المتجر'),
('min_stock_alert', '5', 'حد التنبيه للمخزون المنخفض'),
('vat_rate', '15', 'نسبة ضريبة القيمة المضافة');
```

### 5.3 Initial Cash Balance

```sql
INSERT INTO cash_transactions (transaction_type, amount, balance_before, balance_after, description) VALUES
('DEPOSIT', 0, 0, 0, 'رصيد افتتاحي');
```

---

## 6. Database Triggers | المشغلات

### 6.1 Auto-Update Timestamps

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Applied to: users, categories, suppliers, customers, products, sales, purchases
```

---

*Document reverse-engineered from codebase analysis - March 2026*
