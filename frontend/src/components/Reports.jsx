import { useState, useEffect } from 'react';
import { AnalyticsAPI } from '../services/api';
import {
    AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const PERIOD_OPTIONS = [
    { value: 'week', label: 'أسبوع', labelEn: '1 Week' },
    { value: 'month', label: 'شهر', labelEn: '1 Month' },
    { value: '3months', label: '3 أشهر', labelEn: '3 Months' },
    { value: '6months', label: '6 أشهر', labelEn: '6 Months' },
    { value: 'year', label: 'سنة', labelEn: '1 Year' },
];

function Reports() {
    const [period, setPeriod] = useState('month');
    const [reportData, setReportData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadReportData();
    }, [period]);

    const loadReportData = async () => {
        try {
            setLoading(true);
            const data = await AnalyticsAPI.getFinancialReports(period);
            setReportData(data);
        } catch (error) {
            console.error('Error loading reports:', error);
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (value) => {
        if (value === null || value === undefined) return '0 EGP';
        return Number(value).toLocaleString('en-US') + ' EGP';
    };

    const formatNumber = (value) => {
        if (value === null || value === undefined) return '0';
        return Number(value).toLocaleString('en-US');
    };

    // Custom tooltip for charts
    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <div style={{
                    background: 'white',
                    padding: '12px 16px',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                }}>
                    <p style={{ margin: 0, fontWeight: 600, marginBottom: '8px', color: '#1e293b' }}>{label}</p>
                    {payload.map((entry, index) => (
                        <p key={index} style={{ margin: '4px 0', color: entry.color, fontSize: '0.9rem' }}>
                            {entry.name}: {formatCurrency(entry.value)}
                        </p>
                    ))}
                </div>
            );
        }
        return null;
    };

    // Profit breakdown for pie chart
    const profitBreakdown = reportData ? [
        { name: 'Gross Profit', nameAr: 'الربح الإجمالي', value: reportData.summary.gross_profit, color: '#10b981' },
        { name: 'Purchases', nameAr: 'المشتريات', value: reportData.summary.total_purchases, color: '#6366f1' },
    ].filter(item => item.value > 0) : [];

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>جاري تحميل التقارير...</p>
            </div>
        );
    }

    return (
        <div className="reports-container">
            {/* Header */}
            <div className="page-header">
                <div>
                    <h1><i className="fas fa-chart-bar"></i> تقارير الأرباح والمبيعات</h1>
                    <p className="page-subtitle">
                        من {reportData?.start_date} إلى {reportData?.end_date}
                    </p>
                </div>
            </div>

            {/* Period Selector */}
            <div className="period-selector">
                {PERIOD_OPTIONS.map(opt => (
                    <button
                        key={opt.value}
                        className={`period-btn ${period === opt.value ? 'active' : ''}`}
                        onClick={() => setPeriod(opt.value)}
                    >
                        {opt.label}
                    </button>
                ))}
            </div>

            {/* Summary Cards */}
            {reportData && (
                <div className="summary-cards">
                    <div className="summary-card sales">
                        <div className="card-icon">
                            <i className="fas fa-shopping-cart"></i>
                        </div>
                        <div className="card-content">
                            <span className="label">إجمالي المبيعات</span>
                            <span className="value">{formatCurrency(reportData.summary.total_sales)}</span>
                            <span className="count">{reportData.summary.sales_count} عملية بيع</span>
                        </div>
                    </div>

                    <div className="summary-card purchases">
                        <div className="card-icon">
                            <i className="fas fa-truck"></i>
                        </div>
                        <div className="card-content">
                            <span className="label">إجمالي المشتريات</span>
                            <span className="value">{formatCurrency(reportData.summary.total_purchases)}</span>
                            <span className="count">{reportData.summary.purchases_count} عملية شراء</span>
                        </div>
                    </div>

                    <div className="summary-card profit">
                        <div className="card-icon">
                            <i className="fas fa-hand-holding-usd"></i>
                        </div>
                        <div className="card-content">
                            <span className="label">صافي الربح</span>
                            <span className="value">{formatCurrency(reportData.summary.gross_profit)}</span>
                            <span className="count">هامش الربح: {reportData.summary.profit_margin}%</span>
                        </div>
                    </div>

                    <div className="summary-card margin">
                        <div className="card-icon">
                            <i className="fas fa-percentage"></i>
                        </div>
                        <div className="card-content">
                            <span className="label">هامش الربح</span>
                            <span className="value">{reportData.summary.profit_margin}%</span>
                            <span className="count">Net Profit Margin</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Charts Section */}
            <div className="charts-row">
                {/* Sales vs Purchases Line Chart */}
                <div className="report-chart wide">
                    <div className="chart-header">
                        <h3><i className="fas fa-chart-line"></i> Sales vs Purchases - المبيعات مقابل المشتريات</h3>
                    </div>
                    <div className="chart-body">
                        {reportData?.trend_data?.length > 0 ? (
                            <ResponsiveContainer width="100%" height={350}>
                                <AreaChart data={reportData.trend_data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="salesGrad" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                                            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="purchasesGrad" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="profitGrad" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.4} />
                                            <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                    <XAxis
                                        dataKey="date"
                                        tick={{ fontSize: 11, fill: '#64748b' }}
                                        tickFormatter={(val) => val.includes('-W') ? `W${val.split('-W')[1]}` : val.slice(5)}
                                    />
                                    <YAxis
                                        tick={{ fontSize: 11, fill: '#64748b' }}
                                        tickFormatter={(value) => value > 1000 ? `${(value / 1000).toFixed(0)}K` : value}
                                    />
                                    <Tooltip content={<CustomTooltip />} />
                                    <Legend />
                                    <Area
                                        type="monotone"
                                        dataKey="sales"
                                        name="Sales المبيعات"
                                        stroke="#10b981"
                                        strokeWidth={2}
                                        fill="url(#salesGrad)"
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="purchases"
                                        name="Purchases المشتريات"
                                        stroke="#6366f1"
                                        strokeWidth={2}
                                        fill="url(#purchasesGrad)"
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="profit"
                                        name="Profit الربح"
                                        stroke="#f59e0b"
                                        strokeWidth={2}
                                        fill="url(#profitGrad)"
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="no-data">
                                <i className="fas fa-inbox"></i>
                                <p>لا توجد بيانات للفترة المحددة</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Profit Distribution Pie Chart */}
                <div className="report-chart">
                    <div className="chart-header">
                        <h3><i className="fas fa-chart-pie"></i> Revenue Breakdown - توزيع الإيرادات</h3>
                    </div>
                    <div className="chart-body">
                        {profitBreakdown.length > 0 ? (
                            <>
                                <ResponsiveContainer width="100%" height={220}>
                                    <PieChart>
                                        <Pie
                                            data={profitBreakdown}
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={50}
                                            outerRadius={80}
                                            paddingAngle={3}
                                            dataKey="value"
                                        >
                                            {profitBreakdown.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={entry.color} />
                                            ))}
                                        </Pie>
                                        <Tooltip formatter={(value) => formatCurrency(value)} />
                                    </PieChart>
                                </ResponsiveContainer>
                                <div className="pie-legend">
                                    {profitBreakdown.map((item, index) => (
                                        <div key={index} className="legend-item">
                                            <span className="legend-dot" style={{ background: item.color }}></span>
                                            <span className="legend-label">{item.nameAr}</span>
                                            <span className="legend-value">{formatCurrency(item.value)}</span>
                                        </div>
                                    ))}
                                </div>
                            </>
                        ) : (
                            <div className="no-data">
                                <i className="fas fa-chart-pie"></i>
                                <p>لا توجد بيانات</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Profit Bar Chart */}
            {reportData?.trend_data?.length > 0 && (
                <div className="report-chart full-width">
                    <div className="chart-header">
                        <h3><i className="fas fa-chart-bar"></i> Profit Trend - اتجاه الأرباح</h3>
                    </div>
                    <div className="chart-body">
                        <ResponsiveContainer width="100%" height={280}>
                            <BarChart data={reportData.trend_data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                <XAxis
                                    dataKey="date"
                                    tick={{ fontSize: 11, fill: '#64748b' }}
                                    tickFormatter={(val) => val.includes('-W') ? `W${val.split('-W')[1]}` : val.slice(5)}
                                />
                                <YAxis
                                    tick={{ fontSize: 11, fill: '#64748b' }}
                                    tickFormatter={(value) => value > 1000 ? `${(value / 1000).toFixed(0)}K` : value}
                                />
                                <Tooltip content={<CustomTooltip />} />
                                <Legend />
                                <Bar dataKey="profit" name="Profit الربح" fill="#10b981" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Reports;
