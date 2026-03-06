# Product Requirements Document (PRD)
# وثيقة متطلبات المنتج

**Project:** Sales Management System | نظام إدارة المبيعات  
**Version:** 2.0.0  
**Date:** March 2026  
**Status:** Reverse-Engineered from Codebase

---

## 1. Executive Summary | ملخص تنفيذي

### 1.1 Product Vision
A comprehensive Arabic-first sales management system designed for small to medium retail businesses, specifically tailored for computer and electronics stores in the Egyptian/Arab market.

### 1.2 Target Users
| User Type | Arabic | Description |
|-----------|--------|-------------|
| Admin | مدير | Full system control, user management |
| Manager | مشرف | Sales, purchases, reports (no user management) |
| Cashier | كاشير | Point-of-sale operations only |

### 1.3 Core Value Proposition
- **Arabic-First Interface**: Full RTL support with Arabic UI/UX
- **Integrated Operations**: Sales, purchases, inventory in one system
- **Cash Flow Tracking**: Real-time capital and balance management
- **Role-Based Security**: JWT authentication with granular permissions

---

## 2. Product Goals | أهداف المنتج

### 2.1 Primary Goals (Inferred from Implementation)

| Goal | Implementation Status |
|------|----------------------|
| Manage retail sales with multi-item invoices | ✅ Fully Implemented |
| Track purchases and supplier relationships | ✅ Fully Implemented |
| Real-time inventory management | ✅ Fully Implemented |
| Customer credit/debit tracking | ✅ Fully Implemented |
| Cash/capital flow management | ✅ Fully Implemented |
| Business analytics and KPIs | ✅ Fully Implemented |
| Multi-user role-based access | ✅ Fully Implemented |
| Activity audit logging | ✅ Fully Implemented |

### 2.2 Secondary Goals

| Goal | Implementation Status |
|------|----------------------|
| CSV bulk import/export | ✅ Implemented |
| Invoice printing | ⚠️ Basic (no PDF) |
| Email notifications | ❌ Not Implemented |
| Barcode scanning | ❌ Not Implemented |
| Multi-language support | ❌ Arabic only |
| Mobile app | ❌ Not Implemented |

---

## 3. Functional Requirements | المتطلبات الوظيفية

### 3.1 Authentication & Authorization

**Implemented Features:**
- JWT token-based login/logout
- Password hashing with bcrypt
- Three user roles: admin, manager, cashier
- Token expiration (24 hours configurable)
- Activity logging for all user actions

**API Endpoints:**
- `POST /api/auth/login` - User authentication
- `GET /api/auth/me` - Current user info
- `POST /api/auth/logout` - Logout with logging

### 3.2 Product Management

**Implemented Features:**
- CRUD operations for products
- Auto-generated product codes (PROD001, PROD002...)
- Category and supplier assignment
- Purchase price vs sale price tracking
- Minimum stock level alerts
- CSV import/export with UTF-8 BOM for Arabic Excel

**Business Rules:**
- Product quantity starts at 0 (stock added via purchases only)
- Quantity cannot be directly edited (only via purchases/sales/adjustments)
- Low stock threshold is configurable per product

### 3.3 Sales Management

**Implemented Features:**
- Multi-item sales invoices
- Auto-generated invoice numbers (INV001, INV002...)
- Customer selection or walk-in sales
- Discount application at invoice level
- Partial payment support (credit sales)
- Payment method selection (Cash, Visa, Bank Transfer)
- Automatic inventory deduction
- Cash register auto-update on payment

**Business Rules:**
- Stock validation before sale completion
- Customer balance updated on partial payments
- Manager+ role required for edit/delete
- Cash balance must be sufficient for operations

### 3.4 Purchase Management

**Implemented Features:**
- Multi-item purchase invoices
- Auto-generated purchase numbers (PUR001, PUR002...)
- Supplier selection
- Discount and partial payment tracking
- Automatic inventory increase
- Cash register auto-deduction on payment

**Business Rules:**
- Cash balance validation before payment
- Supplier balance updated on partial payments
- Cannot delete purchase if would result in negative stock
- Manager+ role required for edit/delete

### 3.5 Inventory Management

**Implemented Features:**
- Real-time quantity tracking
- Movement history (sales, purchases, adjustments)
- Manual adjustments with reasons
- Low stock alerts and dashboard warnings
- Inventory value calculation

**Adjustment Types:**
- Add: Increase quantity
- Subtract: Decrease quantity  
- Set: Override to specific quantity

### 3.6 Customer & Supplier Management

**Implemented Features:**
- Full CRUD for both entities
- Auto-generated codes
- Contact information storage
- Balance/credit tracking
- Purchase history aggregation
- Search functionality

### 3.7 Cash/Capital Management

**Implemented Features:**
- Cash balance tracking
- Manual deposits (capital injection)
- Manual withdrawals
- Auto-linked to sales (income)
- Auto-linked to purchases (expense)
- Transaction history with audit trail

### 3.8 Dashboard & Analytics

**Implemented Features:**
- Summary statistics cards
- Sales trend charts (14-day view)
- Top selling products
- Stock health pie chart
- KPI calculations (margins, AOV, growth)
- Financial reports (week/month/quarter/year)
- Low stock alerts list

---

## 4. Non-Functional Requirements | المتطلبات غير الوظيفية

### 4.1 Performance
- Target response time: <500ms for API calls
- Support concurrent users: ~10-20 (current architecture)
- Database queries optimized with indexes

### 4.2 Security
- JWT tokens with expiration
- Bcrypt password hashing (12 rounds)
- SQL injection prevention via ORM
- CORS configured for frontend access
- Role-based endpoint protection

### 4.3 Localization
- RTL layout support
- Arabic UI text throughout
- Arabic date formatting
- Egyptian Pound (EGP) currency display
- UTF-8 encoding for Arabic data

### 4.4 Deployment
- Docker containerization
- Docker Compose orchestration
- Nginx reverse proxy for frontend
- PostgreSQL database
- Production-ready configuration

---

## 5. User Stories | قصص المستخدم

### 5.1 Admin Stories
1. As an admin, I can create new users with specific roles
2. As an admin, I can view all activity logs
3. As an admin, I can manage system settings
4. As an admin, I can deposit/withdraw capital

### 5.2 Manager Stories
1. As a manager, I can create and edit sales invoices
2. As a manager, I can manage purchases and inventory
3. As a manager, I can view all reports and analytics
4. As a manager, I can manage customers and suppliers

### 5.3 Cashier Stories
1. As a cashier, I can create new sales
2. As a cashier, I can view product details and stock
3. As a cashier, I can quick-add customers during checkout

---

## 6. Success Metrics | معايير النجاح

### 6.1 Business Metrics (to track)
- Daily/weekly/monthly sales volume
- Gross and net profit margins
- Inventory turnover rate
- Customer acquisition rate
- Average order value (AOV)

### 6.2 Technical Metrics (to track)
- API response times
- Error rates
- User session duration
- System uptime

---

## 7. Constraints & Assumptions | القيود والافتراضات

### 7.1 Constraints
- Single-store deployment (no multi-tenant)
- Arabic-only interface currently
- No offline mode
- No mobile application
- Desktop-first design

### 7.2 Assumptions
- Users have internet connectivity
- Single currency (EGP)
- Small team (1-10 users)
- Moderate transaction volume (100s per day, not 1000s)

---

## 8. Future Considerations | اعتبارات مستقبلية

Based on codebase analysis, the following are planned but not implemented:

1. **Email Notifications**: Low stock alerts, invoice emails
2. **Barcode Integration**: Scanner support, barcode generation
3. **Advanced Reports**: PDF export, custom date ranges
4. **Multi-Language**: English interface option
5. **Mobile App**: React Native application
6. **Multi-Store**: Multi-tenant architecture

---

*Document reverse-engineered from codebase analysis - March 2026*
