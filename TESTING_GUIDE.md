# Sales Management System - Complete Testing Guide
# نظام إدارة المبيعات - دليل الاختبار الشامل

**Version:** 2.0.0  
**Date:** January 24, 2026  
**Test Environment:** http://localhost:5173 (Dev) / http://localhost:8888 (Prod)

---

## 📋 System Overview / نظرة عامة على النظام

### System Features / مميزات النظام

1. **Multi-User Authentication System** / نظام مستخدمين متعدد
   - Admin, Manager, Cashier roles
   - JWT token-based authentication
   - Activity logging for all actions

2. **Product Management** / إدارة المنتجات
   - CRUD operations
   - CSV Import/Export
   - Category & Supplier assignment
   - Automatic code generation

3. **Sales Management** / إدارة المبيعات
   - Create sales invoices
   - Customer management
   - Inventory auto-deduction
   - Multiple payment methods

4. **Purchase Management** / إدارة المشتريات
   - Create purchase invoices
   - Supplier management
   - Inventory auto-increment
   - Cost tracking

5. **Inventory Control** / التحكم في المخزون
   - Real-time inventory tracking
   - Movement history
   - Manual adjustments
   - Low stock alerts

6. **Analytics & Reports** / التقارير والتحليلات
   - Dashboard with KPIs
   - Sales trends
   - Profit reports
   - Top products/customers
   - Financial reports

7. **Settings Management** / إدارة الإعدادات
   - Business configuration
   - Category management
   - Cash/Capital management

---

## 🎯 Testing Checklist / قائمة الاختبار

### Phase 1: Authentication Testing / اختبار المصادقة

#### Test 1.1: User Login ✓
**Test Cases:**
- [ ✓] Valid admin login (admin/admin123)
- [ ] Valid manager login (manager/manager123)
- [ ✓] Valid cashier login (cashier/cashier123)
- [ ✓] Invalid credentials (wrong password)
- [ ✓] Invalid credentials (non-existent user)
- [ ✓] Inactive user login attempt

**Expected Results:**
- ✓ Successful login redirects to dashboard
- ✓ Token stored in localStorage
- ✓ User info displayed in sidebar
- ✓ Failed login shows Arabic error message
- ✓ Inactive users cannot login

**Test Data:**
```
Admin: admin / admin123
Manager: manager / manager123
Cashier: cashier / cashier123
```

#### Test 1.2: Session Management ✓
- [ ] Token expires after inactivity
- [ ] Auto-logout on 401 error
- [ ] Session persists on page refresh
- [ ] Logout clears token and user data

---

### Phase 2: Product Management / إدارة المنتجات

#### Test 2.1: View Products ✓
- [ ] Display all products in grid/list
- [ ] Show product details (code, name, price, quantity)
- [ ] Display category and supplier information
- [ ] Filter by category
- [ ] Search functionality works

**Test Steps:**
1. Navigate to "كارتة الأصناف" (Products)
2. Verify products are displayed
3. Click on different categories
4. Use search box to find products

#### Test 2.2: Create Product ✓
**Test Cases:**
- [ ] Create product with all required fields
- [ ] Create product without category
- [ ] Create product without supplier
- [ ] Attempt duplicate product code
- [ ] Auto-generate product code

**Test Data:**
```json
{
  "code": "PROD-001",
  "name": "لاب توب HP ProBook",
  "category_id": 1,
  "supplier_id": 1,
  "purchase_price": 15000,
  "sale_price": 18000,
  "quantity": 10,
  "min_quantity": 2,
  "description": "لاب توب HP للأعمال"
}
```

**Expected Results:**
- ✓ Product created successfully
- ✓ Product appears in list
- ✓ Duplicate code shows error
- ✓ Arabic validation messages

#### Test 2.3: Update Product ✓
- [ ] Update product name
- [ ] Update prices
- [ ] Update quantity
- [ ] Change category
- [ ] Change supplier

#### Test 2.4: Delete Product ✓
- [ ] Delete product not used in any transaction
- [ ] Attempt to delete product used in sales (should prevent)
- [ ] Confirm deletion dialog appears
- [ ] Product removed from list

#### Test 2.5: CSV Import/Export ✓
**Test Cases:**
- [ ] Export products to CSV
- [ ] Download CSV file
- [ ] Import valid CSV file
- [ ] Import CSV with invalid data
- [ ] Import CSV with duplicate codes
- [ ] Import CSV with Arabic text

**Sample CSV:**
```csv
Code,Name,Category,Supplier,Purchase Price,Sale Price,Quantity,Min Quantity,Description
PROD-002,ماوس لاسلكي,Electronics,TechSupply,50,75,100,10,ماوس لاسلكي عملي
PROD-003,كيبورد ميكانيكال,Electronics,TechSupply,200,300,50,5,كيبورد ألعاب
```

---

### Phase 3: Sales Management / إدارة المبيعات

#### Test 3.1: Create Sale Invoice ✓
**Test Steps:**
1. Click "مبيعات" (Sales)
2. Click "فاتورة جديدة" (New Invoice)
3. Select/Add customer
4. Add products to invoice
5. Set payment details
6. Submit invoice

**Test Cases:**
- [ ] Create cash sale
- [ ] Create credit sale (partial payment)
- [ ] Add multiple products
- [ ] Apply discount
- [ ] Calculate totals correctly
- [ ] Inventory deducted automatically
- [ ] Invoice number auto-generated

**Test Data:**
```json
{
  "customer_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "unit_price": 18000
    }
  ],
  "discount": 500,
  "paid": 35000,
  "payment_method": "كاش",
  "notes": "بيع مباشر"
}
```

**Expected Results:**
- ✓ Invoice created with unique number
- ✓ Total = (items total - discount)
- ✓ Remaining = (total - paid)
- ✓ Product quantity decreased
- ✓ Inventory movement logged

#### Test 3.2: View Sales ✓
- [ ] Display all sales in table
- [ ] Show invoice details
- [ ] Display customer name
- [ ] Show payment status (paid/pending)
- [ ] Show totals

#### Test 3.3: Print Invoice ✓
- [ ] Print button works
- [ ] Invoice format correct
- [ ] Arabic text displays properly
- [ ] All details included

#### Test 3.4: Edit Sale (Manager Only) ✓
- [ ] Manager can edit sales
- [ ] Cashier cannot edit (permission denied)
- [ ] Inventory adjusts on edit
- [ ] Updated totals recalculated

#### Test 3.5: Delete Sale (Manager Only) ✓
- [ ] Manager can delete sales
- [ ] Cashier cannot delete
- [ ] Inventory restored on deletion
- [ ] Confirmation dialog appears

---

### Phase 4: Purchase Management / إدارة المشتريات

#### Test 4.1: Create Purchase Invoice ✓
**Test Steps:**
1. Navigate to "مشتريات" (Purchases)
2. Click "فاتورة جديدة" (New Invoice)
3. Select supplier
4. Add products
5. Set payment details
6. Submit

**Test Cases:**
- [ ] Create purchase from existing supplier
- [ ] Add products to purchase
- [ ] Calculate totals correctly
- [ ] Inventory increased automatically
- [ ] Purchase number auto-generated

**Test Data:**
```json
{
  "supplier_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 50,
      "unit_price": 15000
    }
  ],
  "discount": 1000,
  "paid": 700000,
  "payment_method": "كاش"
}
```

#### Test 4.2: View Purchases ✓
- [ ] Display all purchases
- [ ] Show supplier information
- [ ] Display payment status
- [ ] Show totals

#### Test 4.3: Edit/Delete Purchase (Manager Only) ✓
- [ ] Manager can edit/delete
- [ ] Inventory adjusts correctly
- [ ] Other roles cannot edit/delete

---

### Phase 5: Customer Management / إدارة العملاء

#### Test 5.1: CRUD Operations ✓
- [ ] View all customers
- [ ] Create new customer
- [ ] Auto-generate customer code
- [ ] Update customer details
- [ ] Delete customer (not used in sales)
- [ ] Search customers

**Test Data:**
```json
{
  "code": "CUST-001",
  "name": "أحمد محمد علي",
  "phone": "01012345678",
  "email": "ahmed@example.com",
  "address": "القاهرة، مصر",
  "notes": "عميل VIP"
}
```

---

### Phase 6: Supplier Management / إدارة الموردين

#### Test 6.1: CRUD Operations ✓
- [ ] View all suppliers
- [ ] Create new supplier
- [ ] Auto-generate supplier code
- [ ] Update supplier details
- [ ] Delete supplier (not used in purchases)
- [ ] Search suppliers

**Test Data:**
```json
{
  "code": "SUP-001",
  "name": "شركة التوريدات التقنية",
  "phone": "01098765432",
  "email": "tech@supply.com",
  "address": "الجيزة، مصر",
  "notes": "مورد رئيسي"
}
```

---

### Phase 7: Inventory Management / إدارة المخزون

#### Test 7.1: View Inventory ✓
- [ ] Display all products with quantities
- [ ] Show low stock items (quantity < min_quantity)
- [ ] Display inventory value
- [ ] Filter by category

#### Test 7.2: Inventory Movements ✓
- [ ] View movement history
- [ ] Filter by product
- [ ] Show movement types (sale/purchase/adjustment)
- [ ] Display before/after quantities

#### Test 7.3: Manual Adjustments ✓
**Test Cases:**
- [ ] Increase inventory (addition)
- [ ] Decrease inventory (damage/loss)
- [ ] Add adjustment reason
- [ ] Verify movement logged

**Test Data:**
```json
{
  "product_id": 1,
  "quantity_change": 5,
  "movement_type": "adjustment",
  "reason": "تالف",
  "notes": "تلف أثناء النقل"
}
```

---

### Phase 8: Dashboard & Analytics / لوحة التحكم

#### Test 8.1: Dashboard Stats ✓
- [ ] Display total sales
- [ ] Show total products
- [ ] Display customer count
- [ ] Show low stock alerts
- [ ] Display cash balance

#### Test 8.2: KPI Cards ✓
- [ ] Today's revenue
- [ ] Profit margin
- [ ] Average order value
- [ ] Growth percentages

#### Test 8.3: Charts & Graphs ✓
- [ ] Sales trend chart (last 14 days)
- [ ] Top products chart
- [ ] Stock health pie chart
- [ ] Financial reports

#### Test 8.4: Recent Sales Table ✓
- [ ] Display last 5 sales
- [ ] Show customer names
- [ ] Display amounts

#### Test 8.5: Low Stock Alerts ✓
- [ ] Display products below minimum
- [ ] Show remaining quantities
- [ ] Highlight critical items

---

### Phase 9: Reports / التقارير

#### Test 9.1: Sales Reports ✓
- [ ] Sales trend (daily/weekly/monthly)
- [ ] Top selling products
- [ ] Customer purchase history
- [ ] Sales by category

#### Test 9.2: Financial Reports ✓
**Test Cases:**
- [ ] Profit report (date range)
- [ ] Income statement
- [ ] Sales vs Purchases comparison
- [ ] Period: Week, Month, 3M, 6M, Year

**Test Steps:**
1. Navigate to "التقارير" (Reports)
2. Select report type
3. Choose date range
4. View charts and data
5. Export report (if available)

#### Test 9.3: Inventory Reports ✓
- [ ] Inventory value report
- [ ] Stock movement report
- [ ] Low stock report
- [ ] Product profitability

---

### Phase 10: Settings / الإعدادات

#### Test 10.1: Business Settings ✓
- [ ] Update company name
- [ ] Change business address
- [ ] Update contact info
- [ ] Set currency
- [ ] Configure tax settings

#### Test 10.2: Category Management ✓
- [ ] View categories
- [ ] Create new category
- [ ] Edit category
- [ ] Delete category (not used by products)

**Test Data:**
```json
{
  "code": "CAT-001",
  "name": "Electronics",
  "name_ar": "إلكترونيات",
  "description": "أجهزة إلكترونية"
}
```

#### Test 10.3: Cash Management ✓
- [ ] View current cash balance
- [ ] Deposit cash (add capital)
- [ ] Withdraw cash
- [ ] View transaction history
- [ ] Verify balance updates

**Test Cases:**
- [ ] Deposit 10,000 EGP
- [ ] Withdraw 5,000 EGP
- [ ] View transactions
- [ ] Check balance = deposits - withdrawals

---

### Phase 11: User Management (Admin Only) / إدارة المستخدمين

#### Test 11.1: View Users ✓
- [ ] Admin can see all users
- [ ] Display user roles
- [ ] Show active/inactive status
- [ ] Show last login

#### Test 11.2: Create User ✓
**Test Cases:**
- [ ] Create admin user
- [ ] Create manager user
- [ ] Create cashier user
- [ ] Duplicate username validation

**Test Data:**
```json
{
  "username": "testuser",
  "password": "Test@123",
  "full_name": "محمد أحمد",
  "role": "cashier"
}
```

#### Test 11.3: Update User ✓
- [ ] Change user name
- [ ] Change user role
- [ ] Reset password
- [ ] Activate/deactivate user

#### Test 11.4: Delete User ✓
- [ ] Delete non-admin user
- [ ] Cannot delete admin user
- [ ] Confirmation dialog

#### Test 11.5: Activity Logs ✓
- [ ] View user activity logs
- [ ] Filter by action type
- [ ] Show timestamps
- [ ] Display entity details

---

## 🔐 Security Testing / اختبار الأمان

### Test S.1: Authentication & Authorization ✓
- [ ] Unauthenticated users redirected to login
- [ ] Expired tokens trigger re-login
- [ ] Role-based access control works
- [ ] Admin-only features blocked for others
- [ ] Manager features blocked for cashier

### Test S.2: Data Validation ✓
- [ ] Required fields validation
- [ ] Email format validation
- [ ] Phone number validation
- [ ] Price must be positive
- [ ] Quantity must be positive
- [ ] Date validation

### Test S.3: SQL Injection Prevention ✓
- [ ] Test special characters in inputs
- [ ] Test SQL keywords in search
- [ ] Verify parameterized queries used

### Test S.4: XSS Prevention ✓
- [ ] Test script tags in text fields
- [ ] Verify output encoding
- [ ] Test HTML injection

---

## 🌐 UI/UX Testing / اختبار واجهة المستخدم

### Test UI.1: Layout & Design ✓
- [ ] Sidebar navigation works
- [ ] Menu items highlighted correctly
- [ ] Content area responsive
- [ ] Cards and tables styled properly
- [ ] No overlapping components

### Test UI.2: Arabic Language Support ✓
- [ ] RTL (Right-to-Left) layout
- [ ] Arabic text displays correctly
- [ ] Forms in Arabic
- [ ] Error messages in Arabic
- [ ] Date format appropriate

### Test UI.3: Responsive Design ✓
- [ ] Desktop view (1920x1080)
- [ ] Laptop view (1366x768)
- [ ] Tablet view (768x1024)
- [ ] Mobile view (375x667)
- [ ] Sidebar collapsible on mobile

### Test UI.4: Icons & Colors ✓
- [ ] Icons load correctly
- [ ] Color scheme consistent
- [ ] Status badges colored appropriately
- [ ] Buttons styled correctly
- [ ] Hover effects work

---

## ⚡ Performance Testing / اختبار الأداء

### Test P.1: Page Load Times ✓
- [ ] Dashboard loads in < 2 seconds
- [ ] Product list loads in < 3 seconds
- [ ] Sales list loads in < 3 seconds
- [ ] Reports generate in < 5 seconds

### Test P.2: Large Data Sets ✓
- [ ] 1000+ products display correctly
- [ ] 500+ sales transactions
- [ ] CSV import of 100+ rows
- [ ] Pagination works properly

### Test P.3: Concurrent Users ✓
- [ ] Multiple users can login
- [ ] Simultaneous transactions
- [ ] No data conflicts
- [ ] Database locking works

---

## 🐛 Error Handling Testing / اختبار معالجة الأخطاء

### Test E.1: Network Errors ✓
- [ ] Backend offline shows error
- [ ] Timeout handling
- [ ] Retry mechanism
- [ ] User-friendly error messages

### Test E.2: Database Errors ✓
- [ ] Connection failure handling
- [ ] Transaction rollback on error
- [ ] Constraint violation messages
- [ ] Foreign key errors

### Test E.3: Validation Errors ✓
- [ ] Required field messages
- [ ] Invalid data format messages
- [ ] Business rule violations
- [ ] Error messages in Arabic

---

## 📱 Browser Compatibility / التوافق مع المتصفحات

### Test B.1: Browser Testing ✓
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Edge (latest)
- [ ] Safari (latest)
- [ ] Opera

### Test B.2: Browser Features ✓
- [ ] LocalStorage works
- [ ] Fetch API works
- [ ] CSS Grid/Flexbox
- [ ] ES6+ JavaScript features

---

## 🔄 Integration Testing / اختبار التكامل

### Test I.1: End-to-End Workflows ✓

**Workflow 1: Complete Sale Process**
1. Login as cashier
2. Add new customer
3. Create sale invoice
4. Add 3 products
5. Apply discount
6. Process payment
7. Print invoice
8. Verify inventory decreased
9. Check dashboard updated

**Workflow 2: Purchase & Stock Management**
1. Login as manager
2. Add new supplier
3. Create purchase order
4. Add products
5. Complete purchase
6. Verify inventory increased
7. Check product prices updated
8. View inventory movements

**Workflow 3: Complete Business Day**
1. Login as admin
2. View dashboard (morning)
3. Process 5 sales
4. Process 2 purchases
5. Add customer payment
6. Generate end-of-day report
7. Check cash balance
8. View activity logs
9. Logout

---

## ✅ Test Results Summary / ملخص نتائج الاختبار

### Pass/Fail Criteria
- **Critical**: Must pass 100%
- **High**: Must pass 95%+
- **Medium**: Must pass 90%+
- **Low**: Must pass 80%+

### Test Coverage
```
Authentication:        [ ] Passed  [ ] Failed  [ ] Skipped
Product Management:    [ ] Passed  [ ] Failed  [ ] Skipped
Sales Management:      [ ] Passed  [ ] Failed  [ ] Skipped
Purchase Management:   [ ] Passed  [ ] Failed  [ ] Skipped
Customer Management:   [ ] Passed  [ ] Failed  [ ] Skipped
Supplier Management:   [ ] Passed  [ ] Failed  [ ] Skipped
Inventory Management:  [ ] Passed  [ ] Failed  [ ] Skipped
Dashboard & Analytics: [ ] Passed  [ ] Failed  [ ] Skipped
Reports:               [ ] Passed  [ ] Failed  [ ] Skipped
Settings:              [ ] Passed  [ ] Failed  [ ] Skipped
User Management:       [ ] Passed  [ ] Failed  [ ] Skipped
Security:              [ ] Passed  [ ] Failed  [ ] Skipped
UI/UX:                 [ ] Passed  [ ] Failed  [ ] Skipped
Performance:           [ ] Passed  [ ] Failed  [ ] Skipped
Error Handling:        [ ] Passed  [ ] Failed  [ ] Skipped
Browser Compatibility: [ ] Passed  [ ] Failed  [ ] Skipped
Integration:           [ ] Passed  [ ] Failed  [ ] Skipped
```

---

## 🐛 Bug Tracking Template / نموذج تتبع الأخطاء

### Bug Report Format
```
Bug ID: BUG-XXX
Title: [Brief description]
Severity: Critical / High / Medium / Low
Module: [Authentication / Products / Sales / etc.]
Reported By: [Your Name]
Date: [YYYY-MM-DD]

Description:
[Detailed description of the issue]

Steps to Reproduce:
1. 
2. 
3. 

Expected Result:
[What should happen]

Actual Result:
[What actually happens]

Environment:
- Browser: 
- OS: 
- Screen Size: 

Screenshots:
[Attach if applicable]

Status: Open / In Progress / Resolved / Closed
```

---

## 📊 Test Metrics / مقاييس الاختبار

### Quality Metrics
- **Test Coverage**: ____%
- **Pass Rate**: ____%
- **Critical Bugs**: ___
- **High Priority Bugs**: ___
- **Medium Priority Bugs**: ___
- **Low Priority Bugs**: ___
- **Average Bug Fix Time**: ___ hours
- **Code Quality Score**: ___/10

---

## 🚀 Deployment Checklist / قائمة نشر النظام

### Pre-Deployment ✓
- [ ] All tests passed
- [ ] No critical bugs
- [ ] Database backed up
- [ ] Environment variables set
- [ ] SSL certificate installed
- [ ] CORS configured
- [ ] Performance optimized
- [ ] Security audit completed

### Post-Deployment ✓
- [ ] Health check passes
- [ ] Login works
- [ ] Database connected
- [ ] API endpoints respond
- [ ] Frontend loads
- [ ] Monitoring enabled
- [ ] Backup scheduled
- [ ] User training completed

---

## 📞 Support & Contact / الدعم والتواصل

### Technical Support
- **Email**: support@example.com
- **Phone**: +20 XXX XXX XXXX
- **Hours**: 9 AM - 5 PM (Cairo Time)

### Documentation
- System Manual: `/docs/manual.pdf`
- API Documentation: http://localhost:8000/docs
- Video Tutorials: [Link]

---

## 📝 Notes / ملاحظات

### Known Limitations
1. Cash API endpoints not yet implemented (planned)
2. Email notifications not configured
3. Multi-language support (Arabic only currently)
4. Mobile app not available

### Future Enhancements
1. Barcode scanner integration
2. Email/SMS notifications
3. Advanced reporting
4. Mobile application
5. Multi-branch support
6. Cloud sync

---

**Testing Started**: ___________  
**Testing Completed**: ___________  
**Tested By**: ___________  
**Approved By**: ___________  

**Overall Status**: [ ] PASS [ ] FAIL [ ] NEEDS REVIEW
