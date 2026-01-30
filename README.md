# نظام إدارة المبيعات | Sales Management System

نظام متكامل لإدارة المبيعات والمشتريات والمخزون مع واجهة عربية كاملة.

A comprehensive sales management system with full Arabic interface for managing sales, purchases, and inventory.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 المميزات | Features

### إدارة المبيعات والمشتريات
- ✅ فواتير بيع وشراء متعددة الأصناف
- ✅ تتبع المدفوعات والمديونيات
- ✅ تحديث المخزون تلقائياً
- ✅ طباعة الفواتير

### إدارة المخزون
- ✅ تتبع الكميات بشكل آني
- ✅ تنبيهات المخزون المنخفض
- ✅ سجل كامل لحركات المخزون
- ✅ تعديل يدوي مع تسجيل السبب

### إدارة رأس المال
- ✅ تتبع رصيد الصندوق
- ✅ إضافة وسحب رأس المال
- ✅ ربط تلقائي مع المبيعات والمشتريات
- ✅ سجل كامل للمعاملات المالية

### لوحة التحكم
- ✅ إحصائيات شاملة
- ✅ رسوم بيانية تفاعلية
- ✅ أفضل المنتجات مبيعاً
- ✅ تقارير الأرباح

### نظام المستخدمين
- ✅ تسجيل دخول آمن (JWT)
- ✅ ثلاث صلاحيات: مدير، مشرف، كاشير
- ✅ سجل نشاطات المستخدمين

## 🛠 التقنيات المستخدمة | Tech Stack

| Frontend | Backend | Database | DevOps |
|----------|---------|----------|--------|
| React 18 | FastAPI | PostgreSQL 15 | Docker |
| Vite 5 | SQLAlchemy | - | Docker Compose |
| Recharts | Pydantic | - | Nginx |
| Axios | JWT Auth | - | - |

## 📋 متطلبات التشغيل | Prerequisites

- Docker & Docker Compose
- Git

## 🚀 التشغيل السريع | Quick Start

### 1. استنساخ المشروع
```bash
git clone https://github.com/yourusername/sales-management-system.git
cd sales-management-system
```

### 2. إعداد ملف البيئة
```bash
cp .env.example .env
# قم بتعديل كلمات المرور في ملف .env
```

### 3. تشغيل النظام
```bash
docker-compose up -d
```

### 4. الوصول للنظام
- **النظام**: http://localhost
- **API**: http://localhost:8000/docs

### بيانات الدخول الافتراضية
- **اسم المستخدم**: `admin`
- **كلمة المرور**: `admin123`

> ⚠️ **مهم**: قم بتغيير كلمة مرور المدير فور تسجيل الدخول

## 🔧 بيئة التطوير | Development

## 🔧 بيئة التطوير | Development

للتطوير، استخدم فرع `dev`:
```bash
git checkout dev
docker-compose up -d
```

يتضمن فرع التطوير:
- Frontend مع Hot Reload على المنفذ 5173
- Backend مع Auto Reload على المنفذ 8000
- PostgreSQL على المنفذ 5432
- pgAdmin على المنفذ 5050

## 📁 هيكل المشروع | Project Structure

```
sales-management-system/
├── backend/
│   ├── main.py          # FastAPI endpoints
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # Database operations
│   ├── auth.py          # JWT authentication
│   ├── database.py      # Database connection
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API services
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── database/
│   └── schema.sql       # Database schema
├── docker-compose.yml        # Development
├── docker-compose.prod.yml   # Production
└── README.md
```

## 📊 الجداول الرئيسية | Database Tables

| الجدول | الوصف |
|--------|-------|
| users | المستخدمين والصلاحيات |
| products | المنتجات والأصناف |
| customers | العملاء |
| suppliers | الموردين |
| sales | فواتير البيع |
| purchases | فواتير الشراء |
| inventory_movements | حركات المخزون |
| cash_transactions | المعاملات المالية |
| settings | إعدادات النظام |

## 🔐 الصلاحيات | User Roles

| الدور | الصلاحيات |
|-------|----------|
| admin | جميع الصلاحيات + إدارة المستخدمين |
| manager | البيع والشراء والتقارير |
| cashier | البيع فقط |

## 📝 API Documentation

بعد تشغيل النظام، يمكنك الوصول لتوثيق API:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🐛 استكشاف الأخطاء | Troubleshooting

### مشكلة في قاعدة البيانات
```bash
# إعادة إنشاء قاعدة البيانات
docker-compose down -v
docker-compose up -d
```

### مشكلة في الحاويات
```bash
# إعادة بناء الحاويات
docker-compose build --no-cache
docker-compose up -d
```

## 📄 الرخصة | License

MIT License - يمكنك استخدام هذا المشروع بحرية.

## 👨‍💻 المساهمة | Contributing

نرحب بمساهماتكم! يرجى فتح Issue أو Pull Request.
