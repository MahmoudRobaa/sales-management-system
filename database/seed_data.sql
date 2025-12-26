-- Seed Data for Sales Management System

-- ============================================
-- CATEGORIES
-- ============================================
INSERT INTO categories (code, name, name_ar) VALUES
('computers', 'Computers', 'أجهزة الكمبيوتر'),
('electrical', 'Electrical Tools', 'الأدوات الكهربائية'),
('satellite', 'Satellite Equipment', 'مستلزمات الدش'),
('accessories', 'Accessories', 'إكسسوارات');

-- ============================================
-- SETTINGS
-- ============================================
INSERT INTO settings (key, value, description) VALUES
('store_name', 'محل الحاسوب والأدوات الكهربائية', 'Store name'),
('store_address', 'شارع الرئيسي - المدينة', 'Store address'),
('store_phone', '01000000000', 'Store phone number'),
('min_stock_alert', '5', 'Minimum stock level for alerts'),
('vat_rate', '15', 'VAT rate percentage');

-- ============================================
-- SUPPLIERS
-- ============================================
INSERT INTO suppliers (code, name, phone, email, address, total_purchases, balance) VALUES
('SUPP001', 'المورد التقني', '01098765432', 'tech@example.com', 'القاهرة', 50000, 0),
('SUPP002', 'شركة الأقمار الصناعية', '01187654321', 'satellite@example.com', 'الجيزة', 30000, 5000),
('SUPP003', 'شركة الأجهزة الكهربائية', '01276543210', 'electrical@example.com', 'الإسكندرية', 25000, 0);

-- ============================================
-- CUSTOMERS
-- ============================================
INSERT INTO customers (code, name, phone, email, address, total_purchases, balance) VALUES
('CUST001', 'أحمد محمد', '01012345678', 'ahmed@example.com', 'القاهرة', 1500, 0),
('CUST002', 'محمد علي', '01123456789', 'mohamed@example.com', 'الجيزة', 3200, 500),
('CUST003', 'سارة خالد', '01234567890', 'sara@example.com', 'الإسكندرية', 800, 0);

-- ============================================
-- PRODUCTS
-- ============================================
INSERT INTO products (code, name, category_id, supplier_id, purchase_price, sale_price, quantity, min_quantity, description) VALUES
('PROD001', 'لوحة مفاتيح لاسلكية', 1, 1, 45, 80, 25, 5, 'لوحة مفاتيح لاسلكية من نوع لوجيتك'),
('PROD002', 'ماوس لاسلكي', 1, 1, 25, 50, 40, 5, 'ماوس لاسلكي من نوع لوجيتك'),
('PROD003', 'ريسيفر ديجيتال', 3, 2, 120, 200, 15, 3, 'ريسيفر ديجيتال عالي الجودة'),
('PROD004', 'سلك HDMI', 4, 1, 15, 30, 60, 10, 'سلك HDMI بطول 2 متر'),
('PROD005', 'مروحة مكتب', 2, 3, 60, 110, 12, 3, 'مروحة مكتب صغيرة');
