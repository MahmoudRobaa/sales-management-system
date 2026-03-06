# API Specifications
# مواصفات الـ API

**Project:** Sales Management System  
**Version:** 2.0.0  
**Base URL:** `/api`  
**Date:** March 2026

---

## 1. Overview | نظرة عامة

### 1.1 API Standards

- **Protocol:** HTTP/HTTPS
- **Format:** JSON
- **Encoding:** UTF-8
- **Authentication:** JWT Bearer tokens
- **API Docs:** Swagger at `/docs`, ReDoc at `/redoc`

### 1.2 Common Headers

| Header | Value | Description |
|--------|-------|-------------|
| Content-Type | application/json | Request body format |
| Authorization | Bearer {token} | JWT authentication |
| Accept | application/json | Response format |

### 1.3 Response Codes

| Code | Meaning | Arabic |
|------|---------|--------|
| 200 | OK | نجاح |
| 201 | Created | تم الإنشاء |
| 400 | Bad Request | طلب غير صالح |
| 401 | Unauthorized | غير مصرح |
| 403 | Forbidden | غير مسموح |
| 404 | Not Found | غير موجود |
| 500 | Server Error | خطأ في الخادم |

---

## 2. Authentication Endpoints | نقاط المصادقة

### 2.1 Login

```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded
```

**Request Body:**
```
username=admin&password=admin123
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "full_name": "مدير النظام",
    "role": "admin"
  }
}
```

**Error (401):**
```json
{
  "detail": "اسم المستخدم أو كلمة المرور غير صحيحة"
}
```

### 2.2 Get Current User

```http
GET /api/auth/me
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "admin",
  "full_name": "مدير النظام",
  "role": "admin",
  "is_active": true,
  "created_at": "2026-01-01T00:00:00",
  "last_login": "2026-03-06T10:30:00"
}
```

### 2.3 Logout

```http
POST /api/auth/logout
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "message": "تم تسجيل الخروج بنجاح"
}
```

---

## 3. User Management Endpoints | إدارة المستخدمين

> **Required Role:** Admin only

### 3.1 List Users

```http
GET /api/users
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "username": "admin",
    "full_name": "مدير النظام",
    "role": "admin",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00",
    "last_login": "2026-03-06T10:30:00"
  }
]
```

### 3.2 Create User

```http
POST /api/users
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "cashier1",
  "password": "securepass123",
  "full_name": "كاشير جديد",
  "role": "cashier"
}
```

**Response (200 OK):**
```json
{
  "id": 2,
  "username": "cashier1",
  "full_name": "كاشير جديد",
  "role": "cashier",
  "is_active": true,
  "created_at": "2026-03-06T11:00:00"
}
```

### 3.3 Update User

```http
PUT /api/users/{user_id}
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "full_name": "كاشير محدث",
  "role": "manager",
  "is_active": true,
  "password": "newpassword123"  // Optional
}
```

### 3.4 Delete User

```http
DELETE /api/users/{user_id}
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "message": "تم حذف المستخدم بنجاح"
}
```

---

## 4. Supplier Endpoints | نقاط الموردين

### 4.1 List Suppliers

```http
GET /api/suppliers?skip=0&limit=100
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "code": "SUPP001",
    "name": "مورد التقنية",
    "phone": "01234567890",
    "email": "supplier@example.com",
    "address": "القاهرة",
    "total_purchases": 50000.00,
    "balance": 5000.00,
    "notes": null,
    "created_at": "2026-01-01T00:00:00",
    "updated_at": "2026-03-01T00:00:00"
  }
]
```

### 4.2 Generate Supplier Code

```http
GET /api/suppliers/generate-code
```

**Response:**
```json
{
  "code": "SUPP005"
}
```

### 4.3 Get Supplier by ID

```http
GET /api/suppliers/{supplier_id}
```

### 4.4 Create Supplier

```http
POST /api/suppliers
Content-Type: application/json
```

**Request Body:**
```json
{
  "code": "SUPP005",
  "name": "مورد جديد",
  "phone": "01234567890",
  "email": "new@supplier.com",
  "address": "الجيزة",
  "notes": "ملاحظات إضافية"
}
```

### 4.5 Update Supplier

```http
PUT /api/suppliers/{supplier_id}
Content-Type: application/json
```

### 4.6 Delete Supplier

```http
DELETE /api/suppliers/{supplier_id}
```

---

## 5. Customer Endpoints | نقاط العملاء

### 5.1 List Customers

```http
GET /api/customers?skip=0&limit=100
```

### 5.2 Generate Customer Code

```http
GET /api/customers/generate-code
```

**Response:**
```json
{
  "code": "CUST010"
}
```

### 5.3 CRUD Operations

Same pattern as Suppliers:
- `GET /api/customers/{customer_id}`
- `POST /api/customers`
- `PUT /api/customers/{customer_id}`
- `DELETE /api/customers/{customer_id}`

---

## 6. Product Endpoints | نقاط المنتجات

### 6.1 List Products

```http
GET /api/products?skip=0&limit=100&category=electronics
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "code": "PROD001",
    "name": "لابتوب HP",
    "category_id": 1,
    "supplier_id": 1,
    "purchase_price": 15000.00,
    "sale_price": 18000.00,
    "quantity": 10,
    "min_quantity": 5,
    "description": "لابتوب HP 15.6 بوصة",
    "category": "إلكترونيات",
    "supplier": "مورد التقنية"
  }
]
```

### 6.2 Generate Product Code

```http
GET /api/products/generate-code
```

**Response:**
```json
{
  "code": "PROD025"
}
```

### 6.3 Create Product

```http
POST /api/products
Content-Type: application/json
```

**Request Body:**
```json
{
  "code": "PROD025",
  "name": "كيبورد لاسلكي",
  "category_id": 2,
  "supplier_id": 1,
  "purchase_price": 200.00,
  "sale_price": 300.00,
  "quantity": 0,
  "min_quantity": 10,
  "description": "كيبورد لاسلكي بلوتوث"
}
```

> **Note:** Quantity is always set to 0 on create. Stock is added via purchases.

### 6.4 Export Products CSV

```http
GET /api/products/export-csv
```

**Response:** CSV file download with UTF-8 BOM encoding

### 6.5 Import Products CSV

```http
POST /api/products/import-csv
Content-Type: multipart/form-data
```

**Request:** File upload with CSV file

**Response:**
```json
{
  "imported": 15,
  "errors": ["Row 5: Code 'PROD001' already exists"],
  "total_errors": 1
}
```

---

## 7. Sales Endpoints | نقاط المبيعات

### 7.1 List Sales

```http
GET /api/sales?skip=0&limit=100
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "invoice_no": "INV001",
    "customer_id": 1,
    "customer_name": "أحمد محمد",
    "sale_date": "2026-03-06",
    "subtotal": 18000.00,
    "discount": 500.00,
    "total": 17500.00,
    "paid": 17500.00,
    "remaining": 0.00,
    "status": "مدفوعة",
    "payment_method": "كاش",
    "notes": null,
    "items": [
      {
        "id": 1,
        "sale_id": 1,
        "product_id": 1,
        "product_name": "لابتوب HP",
        "quantity": 1,
        "unit_price": 18000.00,
        "total": 18000.00
      }
    ],
    "created_at": "2026-03-06T10:00:00",
    "updated_at": "2026-03-06T10:00:00"
  }
]
```

### 7.2 Get Sale by ID

```http
GET /api/sales/{sale_id}
```

### 7.3 Create Sale

```http
POST /api/sales
Authorization: Bearer {token}  // Optional but recommended
Content-Type: application/json
```

**Request Body:**
```json
{
  "customer_id": 1,
  "customer_name": "أحمد محمد",
  "sale_date": "2026-03-06",
  "discount": 500.00,
  "paid": 17500.00,
  "payment_method": "كاش",
  "notes": "ملاحظات البيع",
  "items": [
    {
      "product_id": 1,
      "quantity": 1,
      "unit_price": 18000.00
    }
  ]
}
```

**Business Logic:**
1. Validates product stock availability
2. Generates invoice number (INV001, INV002...)
3. Deducts quantities from inventory
4. Creates inventory movement records
5. Updates customer balance if partial payment
6. Adds to cash balance

**Error (400):**
```json
{
  "detail": "الكمية غير كافية في المخزون. المنتج: لابتوب HP. المتاح: 5"
}
```

### 7.4 Update Sale

```http
PUT /api/sales/{sale_id}
Authorization: Bearer {token}
```

> **Required Role:** Manager or Admin

**Note:** Updates reverse previous inventory changes and apply new ones.

### 7.5 Delete Sale

```http
DELETE /api/sales/{sale_id}
Authorization: Bearer {token}
```

> **Required Role:** Manager or Admin

**Response (200 OK):**
```json
{
  "message": "Sale deleted successfully"
}
```

---

## 8. Purchase Endpoints | نقاط المشتريات

### 8.1 List Purchases

```http
GET /api/purchases?skip=0&limit=100
```

### 8.2 Create Purchase

```http
POST /api/purchases
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "supplier_id": 1,
  "supplier_name": "مورد التقنية",
  "purchase_date": "2026-03-06",
  "discount": 0.00,
  "paid": 15000.00,
  "payment_method": "كاش",
  "notes": null,
  "items": [
    {
      "product_id": 1,
      "quantity": 5,
      "unit_price": 15000.00
    }
  ]
}
```

**Business Logic:**
1. Validates cash balance for payment
2. Generates purchase number (PUR001, PUR002...)
3. Adds quantities to inventory
4. Creates inventory movement records
5. Updates supplier balance if partial payment
6. Deducts from cash balance

### 8.3 Update/Delete Purchase

Same pattern as Sales (Manager+ required)

---

## 9. Inventory Endpoints | نقاط المخزون

### 9.1 Get Inventory Movements

```http
GET /api/inventory/movements?product_id=1&skip=0&limit=100
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "product_id": 1,
    "product_name": "لابتوب HP",
    "movement_type": "purchase",
    "quantity_before": 5,
    "quantity_change": 10,
    "quantity_after": 15,
    "reason": "purchase",
    "reference_type": "purchase",
    "reference_id": 5,
    "notes": null,
    "created_at": "2026-03-06T09:00:00"
  }
]
```

### 9.2 Adjust Inventory

```http
POST /api/inventory/adjust
Content-Type: application/json
```

**Request Body:**
```json
{
  "product_id": 1,
  "adjustment_type": "add",    // "add", "subtract", "set"
  "quantity": 5,
  "reason": "جرد",
  "notes": "تصحيح بعد الجرد الشهري"
}
```

**Response (200 OK):**
```json
{
  "id": 25,
  "product_id": 1,
  "product_name": "لابتوب HP",
  "movement_type": "add",
  "quantity_before": 15,
  "quantity_change": 5,
  "quantity_after": 20,
  "reason": "جرد",
  "reference_type": "adjustment",
  "notes": "تصحيح بعد الجرد الشهري",
  "created_at": "2026-03-06T11:30:00"
}
```

---

## 10. Dashboard & Reports Endpoints | لوحة التحكم

### 10.1 Dashboard Stats

```http
GET /api/dashboard/stats
```

**Response:**
```json
{
  "total_sales": 150000.00,
  "total_products": 45,
  "total_customers": 23,
  "today_profit": 5000.00,
  "low_stock_count": 8
}
```

### 10.2 Low Stock Products

```http
GET /api/dashboard/low-stock
```

**Response:**
```json
[
  {
    "id": 5,
    "name": "ماوس لاسلكي",
    "category": "إلكترونيات",
    "quantity": 2,
    "min_quantity": 10,
    "status": "منخفض جدًا"
  }
]
```

### 10.3 Profit Report

```http
GET /api/reports/profit?from_date=2026-01-01&to_date=2026-03-06
```

**Response:**
```json
{
  "total_sales": 150000.00,
  "total_cost": 100000.00,
  "gross_profit": 50000.00,
  "total_discount": 2000.00,
  "net_profit": 48000.00,
  "sales_count": 50
}
```

---

## 11. Analytics Endpoints | نقاط التحليلات

### 11.1 Sales Trend

```http
GET /api/analytics/sales-trend?period=daily&days=30
```

**Response:**
```json
{
  "data": [
    {
      "date": "2026-03-06",
      "sales": 15000.00,
      "profit": 3000.00,
      "orders": 5
    }
  ],
  "period": "daily"
}
```

### 11.2 Top Products

```http
GET /api/analytics/top-products?limit=10
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "لابتوب HP",
    "quantity_sold": 25,
    "revenue": 450000.00,
    "profit": 75000.00
  }
]
```

### 11.3 Inventory Value

```http
GET /api/analytics/inventory-value
```

**Response:**
```json
{
  "total_items": 45,
  "total_quantity": 500,
  "total_cost_value": 750000.00,
  "total_sale_value": 950000.00,
  "potential_profit": 200000.00,
  "stock_health": {
    "good": 30,
    "low": 10,
    "out": 5
  }
}
```

### 11.4 Business KPIs

```http
GET /api/analytics/kpis
```

**Response:**
```json
{
  "total_revenue": 150000.00,
  "today_revenue": 5000.00,
  "this_week_revenue": 35000.00,
  "this_month_revenue": 150000.00,
  "gross_profit_margin": 33.33,
  "net_profit_margin": 32.00,
  "average_order_value": 3000.00,
  "total_orders": 50,
  "pending_receivables": 10000.00,
  "pending_payables": 5000.00,
  "inventory_value": 750000.00,
  "inventory_items": 45,
  "low_stock_items": 10,
  "out_of_stock_items": 5,
  "revenue_growth": 15.5,
  "orders_growth": 10.2
}
```

### 11.5 Financial Reports

```http
GET /api/analytics/financial-reports?period=month
```

**Parameters:** `period` = week | month | 3months | 6months | year

**Response:**
```json
{
  "period": "month",
  "start_date": "2026-02-06",
  "end_date": "2026-03-06",
  "summary": {
    "total_sales": 150000.00,
    "total_purchases": 100000.00,
    "gross_profit": 50000.00,
    "net_profit": 50000.00,
    "profit_margin": 33.33,
    "sales_count": 50,
    "purchases_count": 10
  },
  "trend_data": [
    {
      "date": "2026-03-01",
      "sales": 5000.00,
      "purchases": 2000.00,
      "profit": 3000.00
    }
  ]
}
```

### 11.6 Top Customers

```http
GET /api/analytics/top-customers?limit=10
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "أحمد محمد",
    "total_purchases": 50000.00,
    "orders_count": 15,
    "balance": 0.00,
    "last_purchase": "2026-03-06"
  }
]
```

---

## 12. Cash Management Endpoints | إدارة النقدية

### 12.1 Get Cash Balance

```http
GET /api/cash/balance
```

**Response:**
```json
{
  "balance": 75000.00,
  "last_updated": "2026-03-06T11:00:00"
}
```

### 12.2 Get Cash Transactions

```http
GET /api/cash/transactions?limit=20
```

**Response:**
```json
[
  {
    "id": 1,
    "transaction_type": "sale",
    "amount": 17500.00,
    "balance_before": 57500.00,
    "balance_after": 75000.00,
    "reference_type": "sale",
    "reference_id": 1,
    "description": "إيرادات من فاتورة بيع #INV001",
    "created_by": 1,
    "created_by_name": "مدير النظام",
    "created_at": "2026-03-06T10:00:00"
  }
]
```

### 12.3 Deposit Cash

```http
POST /api/cash/deposit
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "amount": 10000.00,
  "description": "إضافة رأس مال"
}
```

### 12.4 Withdraw Cash

```http
POST /api/cash/withdraw
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "amount": 5000.00,
  "description": "سحب لمصاريف المحل"
}
```

**Error (400) - Insufficient funds:**
```json
{
  "detail": "الرصيد غير كافٍ. الرصيد المتاح: 75000 EGP"
}
```

---

## 13. Settings Endpoints | نقاط الإعدادات

### 13.1 Get All Settings

```http
GET /api/settings
```

**Response:**
```json
[
  {
    "key": "store_name",
    "value": "محل الحاسوب والأدوات الكهربائية",
    "description": "اسم المتجر",
    "updated_at": "2026-01-01T00:00:00"
  },
  {
    "key": "min_stock_alert",
    "value": "5",
    "description": "حد التنبيه للمخزون المنخفض",
    "updated_at": "2026-01-01T00:00:00"
  }
]
```

### 13.2 Update Settings

```http
PUT /api/settings
Content-Type: application/json
```

**Request Body:**
```json
{
  "settings": [
    { "key": "store_name", "value": "اسم المحل الجديد" },
    { "key": "min_stock_alert", "value": "10" }
  ]
}
```

---

## 14. Activity Logs Endpoints | سجل النشاط

> **Required Role:** Manager or Admin

```http
GET /api/activity-logs?skip=0&limit=100&entity_type=sale
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "username": "admin",
    "action": "create",
    "entity_type": "sale",
    "entity_id": 1,
    "entity_name": "فاتورة بيع #1",
    "details": null,
    "ip_address": "192.168.1.1",
    "created_at": "2026-03-06T10:00:00"
  }
]
```

---

## 15. Health Check | فحص الصحة

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## 16. Error Response Format | صيغة الأخطاء

All errors follow this format:

```json
{
  "detail": "وصف الخطأ باللغة العربية"
}
```

For validation errors:

```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

*Document reverse-engineered from codebase analysis - March 2026*
