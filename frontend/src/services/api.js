import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Handle 401 errors (expired token) and response errors
api.interceptors.response.use(
    (response) => {
        // Ensure response has data, even if empty
        if (response.data === undefined || response.data === null || response.data === '') {
            response.data = {};
        }
        return response;
    },
    (error) => {
        // Handle network errors
        if (!error.response) {
            console.error('Network error:', error.message);
            return Promise.reject({
                message: 'خطأ في الاتصال بالخادم. يرجى التحقق من اتصال الإنترنت.',
                originalError: error
            });
        }
        
        // Handle 401 errors (expired token)
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.reload();
        }
        
        // Handle empty or invalid JSON responses
        if (error.response?.data === undefined || error.response?.data === '') {
            error.response.data = {
                detail: 'حدث خطأ في الخادم',
                status: error.response?.status
            };
        }
        
        return Promise.reject(error);
    }
);

// Suppliers API
export const SuppliersAPI = {
    getAll: () => api.get('/suppliers').then(res => res.data),
    getById: (id) => api.get(`/suppliers/${id}`).then(res => res.data),
    create: (data) => api.post('/suppliers', data).then(res => res.data),
    update: (id, data) => api.put(`/suppliers/${id}`, data).then(res => res.data),
    delete: (id) => api.delete(`/suppliers/${id}`).then(res => res.data),
    getNextCode: () => api.get('/suppliers/generate-code').then(res => res.data.code),
};

// Customers API
export const CustomersAPI = {
    getAll: () => api.get('/customers').then(res => res.data),
    getById: (id) => api.get(`/customers/${id}`).then(res => res.data),
    create: (data) => api.post('/customers', data).then(res => res.data),
    update: (id, data) => api.put(`/customers/${id}`, data).then(res => res.data),
    delete: (id) => api.delete(`/customers/${id}`).then(res => res.data),
    getNextCode: () => api.get('/customers/generate-code').then(res => res.data.code),
    // Sprint 5 — Loyalty
    getLoyalty: (id) => api.get(`/customers/${id}/loyalty`).then(res => res.data),
    earnPoints: (id, amount) => api.post(`/customers/${id}/loyalty/earn?amount=${amount}`).then(res => res.data),
    redeemPoints: (id, points) => api.post(`/customers/${id}/loyalty/redeem?points=${points}`).then(res => res.data),
    // Sprint 5 — Purchase History
    getHistory: (id, skip = 0, limit = 50) => api.get(`/customers/${id}/history?skip=${skip}&limit=${limit}`).then(res => res.data),
};

// Products API
export const ProductsAPI = {
    getAll: (category = null) => {
        const params = category && category !== 'all' ? `?category=${category}` : '';
        return api.get(`/products${params}`).then(res => res.data);
    },
    getById: (id) => api.get(`/products/${id}`).then(res => res.data),
    create: (data) => api.post('/products', data).then(res => res.data),
    update: (id, data) => api.put(`/products/${id}`, data).then(res => res.data),
    delete: (id) => api.delete(`/products/${id}`).then(res => res.data),
    exportCSV: () => {
        window.open('http://localhost:8000/api/products/export-csv', '_blank');
    },
    importCSV: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/products/import-csv', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        }).then(res => res.data);
    },
    // Sprint 5 — Barcode lookup
    lookupBarcode: (barcode) => api.get(`/products/barcode/${barcode}`).then(res => res.data),
    // Sprint 5 — Variants
    getVariants: (productId) => api.get(`/products/${productId}/variants`).then(res => res.data),
    createVariant: (productId, data) => api.post(`/products/${productId}/variants`, data).then(res => res.data),
    updateVariant: (productId, variantId, data) => api.put(`/products/${productId}/variants/${variantId}`, data).then(res => res.data),
    deleteVariant: (productId, variantId) => api.delete(`/products/${productId}/variants/${variantId}`).then(res => res.data),
};

// Sales API
export const SalesAPI = {
    getAll: () => api.get('/sales').then(res => res.data),
    getById: (id) => api.get(`/sales/${id}`).then(res => res.data),
    create: (data) => api.post('/sales', data).then(res => res.data),
    update: (id, data) => api.put(`/sales/${id}`, data).then(res => res.data),
    delete: (id) => api.delete(`/sales/${id}`).then(res => res.data),
    // Sprint 5 — Held sales
    getHeld: () => api.get('/sales/held').then(res => res.data),
    resume: (id) => api.put(`/sales/${id}/resume`).then(res => res.data),
};

// Purchases API
export const PurchasesAPI = {
    getAll: () => api.get('/purchases').then(res => res.data),
    getById: (id) => api.get(`/purchases/${id}`).then(res => res.data),
    create: (data) => api.post('/purchases', data).then(res => res.data),
    update: (id, data) => api.put(`/purchases/${id}`, data).then(res => res.data),
    delete: (id) => api.delete(`/purchases/${id}`).then(res => res.data),
};

// Inventory API
export const InventoryAPI = {
    getMovements: (productId = null) => {
        const params = productId ? `?product_id=${productId}` : '';
        return api.get(`/inventory/movements${params}`).then(res => res.data);
    },
    adjust: (data) => api.post('/inventory/adjust', data).then(res => res.data),
};

// Settings API
export const SettingsAPI = {
    getAll: () => api.get('/settings').then(res => res.data),
    update: (settings) => api.put('/settings', { settings }).then(res => res.data),
};

// Dashboard API
export const DashboardAPI = {
    getStats: () => api.get('/dashboard/stats').then(res => res.data),
    getLowStock: () => api.get('/dashboard/low-stock').then(res => res.data),
    getProfitReport: (fromDate = null, toDate = null) => {
        let params = [];
        if (fromDate) params.push(`from_date=${fromDate}`);
        if (toDate) params.push(`to_date=${toDate}`);
        const queryString = params.length > 0 ? `?${params.join('&')}` : '';
        return api.get(`/reports/profit${queryString}`).then(res => res.data);
    },
};

// Analytics API
export const AnalyticsAPI = {
    getSalesTrend: (days = 30) => api.get(`/analytics/sales-trend?days=${days}`).then(res => res.data),
    getTopProducts: (limit = 10) => api.get(`/analytics/top-products?limit=${limit}`).then(res => res.data),
    getInventoryValue: () => api.get('/analytics/inventory-value').then(res => res.data),
    getKPIs: () => api.get('/analytics/kpis').then(res => res.data),
    getTopCustomers: (limit = 10) => api.get(`/analytics/top-customers?limit=${limit}`).then(res => res.data),
    getFinancialReports: (period = 'month') => api.get(`/analytics/financial-reports?period=${period}`).then(res => res.data),
};

// Cash Management API
export const CashAPI = {
    getBalance: () => api.get('/cash/balance').then(res => res.data),
    getTransactions: (limit = 20) => api.get(`/cash/transactions?limit=${limit}`).then(res => res.data),
    deposit: (amount, description = '') => api.post('/cash/deposit', { amount, description }).then(res => res.data),
    withdraw: (amount, description = '') => api.post('/cash/withdraw', { amount, description }).then(res => res.data),
};

// =====================================================
// SPRINT 5 — NEW API MODULES
// =====================================================

// Returns / Refunds API
export const ReturnsAPI = {
    getAll: () => api.get('/returns').then(res => res.data),
    getById: (id) => api.get(`/returns/${id}`).then(res => res.data),
    create: (data) => api.post('/returns', data).then(res => res.data),
    approve: (id) => api.put(`/returns/${id}/approve`).then(res => res.data),
};

// Shift Management API
export const ShiftsAPI = {
    getAll: () => api.get('/shifts').then(res => res.data),
    getCurrent: () => api.get('/shifts/current').then(res => res.data),
    open: (data) => api.post('/shifts/open', data).then(res => res.data),
    close: (data) => api.post('/shifts/close', data).then(res => res.data),
    getById: (id) => api.get(`/shifts/${id}`).then(res => res.data),
    getReconciliation: (id) => api.get(`/shifts/${id}/reconciliation`).then(res => res.data),
    addDrawerLog: (data) => api.post('/shifts/drawer-log', data).then(res => res.data),
    getDrawerLogs: (shiftId) => api.get(`/shifts/drawer-logs?shift_id=${shiftId}`).then(res => res.data),
};

// Installments (Credit Sales) API
export const InstallmentsAPI = {
    getAll: (saleId = null, customerId = null) => {
        const params = [];
        if (saleId) params.push(`sale_id=${saleId}`);
        if (customerId) params.push(`customer_id=${customerId}`);
        const qs = params.length ? `?${params.join('&')}` : '';
        return api.get(`/installments${qs}`).then(res => res.data);
    },
    create: (data) => api.post('/installments', data).then(res => res.data),
    pay: (id) => api.put(`/installments/${id}/pay`).then(res => res.data),
    getOverdue: () => api.get('/installments/overdue').then(res => res.data),
};

// Batch / Expiry Tracking API
export const BatchesAPI = {
    getAll: (productId = null) => {
        const qs = productId ? `?product_id=${productId}` : '';
        return api.get(`/batches${qs}`).then(res => res.data);
    },
    create: (data) => api.post('/batches', data).then(res => res.data),
    getExpiring: (days = 30) => api.get(`/batches/expiring?days=${days}`).then(res => res.data),
    delete: (id) => api.delete(`/batches/${id}`).then(res => res.data),
};

// Stocktake API
export const StocktakeAPI = {
    getAll: () => api.get('/stocktakes').then(res => res.data),
    create: () => api.post('/stocktakes').then(res => res.data),
    getById: (id) => api.get(`/stocktakes/${id}`).then(res => res.data),
    updateCount: (id, data) => api.put(`/stocktakes/${id}/count`, data).then(res => res.data),
    complete: (id) => api.post(`/stocktakes/${id}/complete`).then(res => res.data),
};

// E-Invoice (ETA) API
export const EInvoiceAPI = {
    submit: (saleId) => api.post('/einvoice/submit', { sale_id: saleId }).then(res => res.data),
    getStatus: (saleId) => api.get(`/einvoice/${saleId}`).then(res => res.data),
    getQR: (saleId) => `/api/einvoice/${saleId}/qr`,
};

// Invoicing (PDF / Receipt) API
export const InvoicingAPI = {
    getPDFUrl: (saleId) => `/api/invoice/${saleId}/pdf`,
    getReceiptUrl: (saleId) => `/api/invoice/${saleId}/receipt`,
    getQRUrl: (saleId) => `/api/invoice/${saleId}/qr`,
};

// Advanced Reports API
export const ReportsAdvancedAPI = {
    getHourlyHeatmap: (days = 30) => api.get(`/reports/hourly-heatmap?days=${days}`).then(res => res.data),
    getDeadStock: (days = 90) => api.get(`/reports/dead-stock?days=${days}`).then(res => res.data),
    getMargins: (categoryId = null) => {
        const qs = categoryId ? `?category_id=${categoryId}` : '';
        return api.get(`/reports/margins${qs}`).then(res => res.data);
    },
    getCashierPerformance: (fromDate = null, toDate = null) => {
        const params = [];
        if (fromDate) params.push(`from_date=${fromDate}`);
        if (toDate) params.push(`to_date=${toDate}`);
        const qs = params.length ? `?${params.join('&')}` : '';
        return api.get(`/reports/cashier-performance${qs}`).then(res => res.data);
    },
    getReorderAlerts: () => api.get('/reports/reorder-alerts').then(res => res.data),
    generateAutoPO: () => api.post('/reports/auto-po-draft').then(res => res.data),
};

// Backup API
export const BackupAPI = {
    downloadUrl: () => '/api/backup/download',
    restore: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/backup/restore', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        }).then(res => res.data);
    },
    getInfo: () => api.get('/backup/info').then(res => res.data),
};

export default api;

