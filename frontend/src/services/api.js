import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Categories API
export const CategoriesAPI = {
    getAll: () => api.get('/categories').then(res => res.data),
    getById: (id) => api.get(`/categories/${id}`).then(res => res.data),
    create: (data) => api.post('/categories', data).then(res => res.data),
    update: (id, data) => api.put(`/categories/${id}`, data).then(res => res.data),
    delete: (id) => api.delete(`/categories/${id}`).then(res => res.data),
};

// Suppliers API
export const SuppliersAPI = {
    getAll: () => api.get('/suppliers').then(res => res.data),
    getById: (id) => api.get(`/suppliers/${id}`).then(res => res.data),
    create: (data) => api.post('/suppliers', data).then(res => res.data),
    update: (id, data) => api.put(`/suppliers/${id}`, data).then(res => res.data),
    delete: (id) => api.delete(`/suppliers/${id}`).then(res => res.data),
};

// Customers API
export const CustomersAPI = {
    getAll: () => api.get('/customers').then(res => res.data),
    getById: (id) => api.get(`/customers/${id}`).then(res => res.data),
    create: (data) => api.post('/customers', data).then(res => res.data),
    update: (id, data) => api.put(`/customers/${id}`, data).then(res => res.data),
    delete: (id) => api.delete(`/customers/${id}`).then(res => res.data),
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
};

// Sales API
export const SalesAPI = {
    getAll: () => api.get('/sales').then(res => res.data),
    getById: (id) => api.get(`/sales/${id}`).then(res => res.data),
    create: (data) => api.post('/sales', data).then(res => res.data),
    delete: (id) => api.delete(`/sales/${id}`).then(res => res.data),
};

// Purchases API
export const PurchasesAPI = {
    getAll: () => api.get('/purchases').then(res => res.data),
    getById: (id) => api.get(`/purchases/${id}`).then(res => res.data),
    create: (data) => api.post('/purchases', data).then(res => res.data),
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
};

export default api;
