import { useState, useEffect } from 'react';
import { DashboardAPI, SalesAPI, AnalyticsAPI } from '../services/api';
import {
    AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

function Dashboard() {
    const [stats, setStats] = useState(null);
    const [kpis, setKpis] = useState(null);
    const [salesTrend, setSalesTrend] = useState([]);
    const [topProducts, setTopProducts] = useState([]);
    const [inventoryHealth, setInventoryHealth] = useState(null);
    const [lowStock, setLowStock] = useState([]);
    const [recentSales, setRecentSales] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            setLoading(true);
            setError(null);

            const [statsData, lowStockData, salesData] = await Promise.all([
                DashboardAPI.getStats().catch(() => null),
                DashboardAPI.getLowStock().catch(() => []),
                SalesAPI.getAll().catch(() => [])
            ]);

            setStats(statsData);
            setLowStock(lowStockData || []);
            setRecentSales((salesData || []).slice(0, 5));

            try {
                const [kpisData, trendData, productsData, inventoryData] = await Promise.all([
                    AnalyticsAPI.getKPIs(),
                    AnalyticsAPI.getSalesTrend(14),
                    AnalyticsAPI.getTopProducts(5),
                    AnalyticsAPI.getInventoryValue()
                ]);

                setKpis(kpisData);
                // Format trend data with simpler date format
                const formattedTrend = (trendData?.data || []).map(item => ({
                    ...item,
                    displayDate: item.date ? item.date.slice(5) : '', // MM-DD format
                    sales: Number(item.sales) || 0,
                    profit: Number(item.profit) || 0
                }));
                setSalesTrend(formattedTrend);
                setTopProducts(productsData || []);
                setInventoryHealth(inventoryData);
            } catch (analyticsError) {
                console.warn('Analytics APIs not available:', analyticsError);
            }

        } catch (err) {
            console.error('Error loading dashboard:', err);
            setError('حدث خطأ أثناء تحميل البيانات');
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (value) => {
        if (value === null || value === undefined) return '0 EGP';
        const num = Number(value) || 0;
        return num.toLocaleString('en-US') + ' EGP';
    };

    const formatCurrencyArabic = (value) => {
        if (value === null || value === undefined) return '٠ ج.م';
        return new Intl.NumberFormat('ar-EG', {
            style: 'currency',
            currency: 'EGP',
            minimumFractionDigits: 0
        }).format(value);
    };

    const formatNumber = (value) => {
        if (value === null || value === undefined) return '0';
        return Number(value).toLocaleString('en-US');
    };

    const formatPercent = (value) => {
        if (value === null || value === undefined) return '+0.0%';
        const num = Number(value) || 0;
        const sign = num >= 0 ? '+' : '';
        return `${sign}${num.toFixed(1)}%`;
    };

    const getGrowthClass = (value) => {
        const num = Number(value) || 0;
        return num >= 0 ? 'kpi-growth positive' : 'kpi-growth negative';
    };

    // Custom tooltip for charts
    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <div style={{
                    background: 'white',
                    padding: '12px',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                }}>
                    <p style={{ margin: 0, fontWeight: 600, marginBottom: '8px' }}>{label}</p>
                    {payload.map((entry, index) => (
                        <p key={index} style={{ margin: '4px 0', color: entry.color }}>
                            {entry.name}: {formatCurrency(entry.value)}
                        </p>
                    ))}
                </div>
            );
        }
        return null;
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>جاري التحميل...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
                <i className="fas fa-exclamation-triangle" style={{ fontSize: '3rem', color: '#f59e0b' }}></i>
                <p style={{ marginTop: '20px', color: '#64748b' }}>{error}</p>
                <button className="btn btn-primary" onClick={loadDashboardData} style={{ marginTop: '15px' }}>
                    إعادة المحاولة
                </button>
            </div>
        );
    }

    // Stock health data for pie chart
    const stockHealthData = inventoryHealth?.stock_health ? [
        { name: 'Good Stock', value: inventoryHealth.stock_health.good || 0, color: '#10b981', nameAr: 'مخزون جيد' },
        { name: 'Low Stock', value: inventoryHealth.stock_health.low || 0, color: '#f59e0b', nameAr: 'منخفض' },
        { name: 'Out of Stock', value: inventoryHealth.stock_health.out || 0, color: '#ef4444', nameAr: 'نفذ' }
    ].filter(item => item.value > 0) : [];

    return (
        <div className="dashboard-container">
            {/* Header */}
            <div className="dashboard-header">
                <h2>
                    <i className="fas fa-chart-line"></i>
                    لوحة التحكم
                </h2>
                <button className="btn btn-primary btn-sm" onClick={loadDashboardData}>
                    <i className="fas fa-sync-alt"></i>
                    تحديث
                </button>
            </div>

            {/* Main Stats Cards */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon blue">
                        <i className="fas fa-coins"></i>
                    </div>
                    <div className="stat-info">
                        <h3>{formatNumber(stats?.total_sales || kpis?.total_revenue || 0)}</h3>
                        <p>إجمالي المبيعات (EGP)</p>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon green">
                        <i className="fas fa-box"></i>
                    </div>
                    <div className="stat-info">
                        <h3>{stats?.total_products || kpis?.inventory_items || 0}</h3>
                        <p>عدد المنتجات</p>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon orange">
                        <i className="fas fa-users"></i>
                    </div>
                    <div className="stat-info">
                        <h3>{stats?.total_customers || 0}</h3>
                        <p>عدد العملاء</p>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon red">
                        <i className="fas fa-exclamation-triangle"></i>
                    </div>
                    <div className="stat-info">
                        <h3>{stats?.low_stock_count || kpis?.low_stock_items || 0}</h3>
                        <p>تنبيهات المخزون</p>
                    </div>
                </div>
            </div>

            {/* KPI Cards Row */}
            {kpis && (
                <div className="kpi-row">
                    <div className="kpi-card primary">
                        <div className="kpi-header">
                            <i className="fas fa-calendar-day"></i>
                            <span>إيرادات اليوم</span>
                        </div>
                        <div className="kpi-value-large">{formatNumber(kpis.today_revenue)} EGP</div>
                        <div className={getGrowthClass(kpis.revenue_growth)}>
                            <i className={`fas fa-arrow-${(kpis.revenue_growth || 0) >= 0 ? 'up' : 'down'}`}></i>
                            {formatPercent(kpis.revenue_growth)}
                        </div>
                    </div>

                    <div className="kpi-card success">
                        <div className="kpi-header">
                            <i className="fas fa-percentage"></i>
                            <span>هامش الربح</span>
                        </div>
                        <div className="kpi-value-large">{kpis.net_profit_margin || 0}%</div>
                        <div className="kpi-subtitle">Gross: {kpis.gross_profit_margin || 0}%</div>
                    </div>

                    <div className="kpi-card info">
                        <div className="kpi-header">
                            <i className="fas fa-receipt"></i>
                            <span>متوسط الطلب</span>
                        </div>
                        <div className="kpi-value-large">{formatNumber(kpis.average_order_value)} EGP</div>
                        <div className="kpi-subtitle">{kpis.total_orders || 0} Orders</div>
                    </div>

                    <div className="kpi-card warning">
                        <div className="kpi-header">
                            <i className="fas fa-wallet"></i>
                            <span>مستحقات العملاء</span>
                        </div>
                        <div className="kpi-value-large">{formatNumber(kpis.pending_receivables)} EGP</div>
                        <div className="kpi-subtitle">Unpaid Balance</div>
                    </div>
                </div>
            )}

            {/* Charts Section */}
            <div className="charts-section">
                {/* Sales Trend Chart */}
                {salesTrend.length > 0 && (
                    <div className="chart-card wide">
                        <div className="chart-header">
                            <h3><i className="fas fa-chart-area"></i> Sales Trend - اتجاه المبيعات</h3>
                            <span className="chart-subtitle">Last 14 Days</span>
                        </div>
                        <div className="chart-body">
                            <ResponsiveContainer width="100%" height={280}>
                                <AreaChart data={salesTrend} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="profitGradient" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                                            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                    <XAxis
                                        dataKey="displayDate"
                                        tick={{ fontSize: 11, fill: '#64748b' }}
                                        axisLine={{ stroke: '#e5e7eb' }}
                                    />
                                    <YAxis
                                        tick={{ fontSize: 11, fill: '#64748b' }}
                                        axisLine={{ stroke: '#e5e7eb' }}
                                        tickFormatter={(value) => value > 1000 ? `${(value / 1000).toFixed(0)}K` : value}
                                    />
                                    <Tooltip content={<CustomTooltip />} />
                                    <Legend
                                        wrapperStyle={{ paddingTop: '15px' }}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="sales"
                                        name="Sales"
                                        stroke="#6366f1"
                                        strokeWidth={2}
                                        fill="url(#salesGradient)"
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="profit"
                                        name="Profit"
                                        stroke="#10b981"
                                        strokeWidth={2}
                                        fill="url(#profitGradient)"
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                )}

                {/* Stock Health Pie Chart */}
                {stockHealthData.length > 0 && (
                    <div className="chart-card">
                        <div className="chart-header">
                            <h3><i className="fas fa-box-open"></i> Stock Health - صحة المخزون</h3>
                        </div>
                        <div className="chart-body">
                            <ResponsiveContainer width="100%" height={220}>
                                <PieChart>
                                    <Pie
                                        data={stockHealthData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={50}
                                        outerRadius={80}
                                        paddingAngle={3}
                                        dataKey="value"
                                    >
                                        {stockHealthData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip formatter={(value, name) => [value, name]} />
                                </PieChart>
                            </ResponsiveContainer>
                            <div className="pie-legend">
                                {stockHealthData.map((item, index) => (
                                    <div key={index} className="legend-item">
                                        <span className="legend-dot" style={{ background: item.color }}></span>
                                        <span className="legend-label">{item.nameAr}</span>
                                        <span className="legend-value">{item.value}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Top Products Chart */}
            {topProducts.length > 0 && (
                <div className="chart-card full">
                    <div className="chart-header">
                        <h3><i className="fas fa-star"></i> Top Selling Products - الأكثر مبيعاً</h3>
                    </div>
                    <div className="chart-body">
                        <ResponsiveContainer width="100%" height={topProducts.length * 60 + 40}>
                            <BarChart
                                data={topProducts}
                                layout="vertical"
                                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                            >
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                <XAxis
                                    type="number"
                                    tick={{ fontSize: 11, fill: '#64748b' }}
                                    tickFormatter={(value) => value > 1000 ? `${(value / 1000).toFixed(0)}K` : value}
                                />
                                <YAxis
                                    type="category"
                                    dataKey="name"
                                    width={140}
                                    tick={{ fontSize: 11, fill: '#1e293b' }}
                                />
                                <Tooltip
                                    formatter={(value, name) => [
                                        name === 'revenue' ? formatCurrency(value) : value,
                                        name === 'revenue' ? 'Revenue' : 'Qty Sold'
                                    ]}
                                />
                                <Legend />
                                <Bar
                                    dataKey="revenue"
                                    name="Revenue (EGP)"
                                    fill="#6366f1"
                                    radius={[0, 4, 4, 0]}
                                    barSize={20}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}

            {/* Data Tables */}
            <div className="tables-section">
                {/* Recent Sales */}
                <div className="table-card">
                    <div className="table-header">
                        <h3><i className="fas fa-receipt"></i> آخر المبيعات</h3>
                    </div>
                    <div className="table-body">
                        <table>
                            <thead>
                                <tr>
                                    <th>الفاتورة</th>
                                    <th>العميل</th>
                                    <th>الإجمالي</th>
                                    <th>الحالة</th>
                                </tr>
                            </thead>
                            <tbody>
                                {recentSales.map(sale => (
                                    <tr key={sale.id}>
                                        <td><strong>{sale.invoice_no}</strong></td>
                                        <td>{sale.customer_name}</td>
                                        <td>{formatCurrencyArabic(sale.total)}</td>
                                        <td>
                                            <span className={`status-badge ${sale.status === 'مدفوعة' ? 'paid' :
                                                    sale.status === 'جزئي' ? 'partial' : 'unpaid'
                                                }`}>
                                                {sale.status}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                                {recentSales.length === 0 && (
                                    <tr><td colSpan="4" className="empty-msg">لا توجد مبيعات</td></tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Low Stock Alerts */}
                <div className="table-card">
                    <div className="table-header warning">
                        <h3><i className="fas fa-exclamation-triangle"></i> تنبيهات المخزون</h3>
                    </div>
                    <div className="table-body">
                        <table>
                            <thead>
                                <tr>
                                    <th>المنتج</th>
                                    <th>الكمية</th>
                                    <th>الحد الأدنى</th>
                                    <th>الحالة</th>
                                </tr>
                            </thead>
                            <tbody>
                                {lowStock.map(product => (
                                    <tr key={product.id}>
                                        <td><strong>{product.name}</strong></td>
                                        <td className="center">{product.quantity}</td>
                                        <td className="center">{product.min_quantity}</td>
                                        <td>
                                            <span className={`status-badge ${product.quantity === 0 ? 'out' : 'low'
                                                }`}>
                                                {product.status}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                                {lowStock.length === 0 && (
                                    <tr><td colSpan="4" className="empty-msg success">✓ جميع المنتجات متوفرة</td></tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Inventory Value Summary */}
            {inventoryHealth && (
                <div className="summary-card">
                    <div className="summary-header">
                        <h3><i className="fas fa-calculator"></i> ملخص المخزون المالي</h3>
                    </div>
                    <div className="summary-grid">
                        <div className="summary-item">
                            <span className="label">تكلفة المخزون</span>
                            <span className="value">{formatNumber(inventoryHealth.total_cost_value)} EGP</span>
                        </div>
                        <div className="summary-item">
                            <span className="label">قيمة البيع</span>
                            <span className="value">{formatNumber(inventoryHealth.total_sale_value)} EGP</span>
                        </div>
                        <div className="summary-item highlight">
                            <span className="label">الربح المحتمل</span>
                            <span className="value success">{formatNumber(inventoryHealth.potential_profit)} EGP</span>
                        </div>
                        <div className="summary-item">
                            <span className="label">إجمالي الوحدات</span>
                            <span className="value">{formatNumber(inventoryHealth.total_quantity)}</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Dashboard;
