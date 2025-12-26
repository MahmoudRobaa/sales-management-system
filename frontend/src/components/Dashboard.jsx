import { useState, useEffect } from 'react'
import { DashboardAPI, SalesAPI } from '../services/api'

function Dashboard() {
    const [stats, setStats] = useState({
        total_sales: 0,
        total_products: 0,
        total_customers: 0,
        today_profit: 0,
        low_stock_count: 0
    })
    const [lowStock, setLowStock] = useState([])
    const [recentSales, setRecentSales] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadDashboardData()
    }, [])

    const loadDashboardData = async () => {
        try {
            setLoading(true)
            const [statsData, lowStockData, salesData] = await Promise.all([
                DashboardAPI.getStats(),
                DashboardAPI.getLowStock(),
                SalesAPI.getAll()
            ])
            setStats(statsData)
            setLowStock(lowStockData)
            setRecentSales(salesData.slice(0, 5))
        } catch (error) {
            console.error('Error loading dashboard:', error)
        } finally {
            setLoading(false)
        }
    }

    const formatCurrency = (amount) => {
        return parseFloat(amount || 0).toFixed(2) + ' ج.م'
    }

    const getStatusClass = (status) => {
        if (status === 'مدفوعة') return 'success'
        if (status === 'جزئي') return 'info'
        return 'danger'
    }

    if (loading) {
        return (
            <div className="loading">
                <div className="loading-spinner"></div>
                <span>جاري التحميل...</span>
            </div>
        )
    }

    return (
        <>
            <div className="page-header">
                <h1>لوحة التحكم</h1>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <i className="fas fa-user-circle" style={{ fontSize: '1.5rem', color: '#7f8c8d' }}></i>
                    <span>مدير النظام</span>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon blue">
                        <i className="fas fa-money-bill-wave"></i>
                    </div>
                    <div className="stat-info">
                        <h3>{formatCurrency(stats.total_sales)}</h3>
                        <p>إجمالي المبيعات</p>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon green">
                        <i className="fas fa-box"></i>
                    </div>
                    <div className="stat-info">
                        <h3>{stats.total_products}</h3>
                        <p>إجمالي الأصناف</p>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon red">
                        <i className="fas fa-users"></i>
                    </div>
                    <div className="stat-info">
                        <h3>{stats.total_customers}</h3>
                        <p>إجمالي العملاء</p>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon orange">
                        <i className="fas fa-chart-line"></i>
                    </div>
                    <div className="stat-info">
                        <h3>{formatCurrency(stats.today_profit)}</h3>
                        <p>أرباح اليوم</p>
                    </div>
                </div>
            </div>

            {/* Recent Sales */}
            <div className="card">
                <div className="card-header">
                    <h2>آخر المبيعات</h2>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>رقم الفاتورة</th>
                            <th>التاريخ</th>
                            <th>العميل</th>
                            <th>المبلغ</th>
                            <th>الحالة</th>
                        </tr>
                    </thead>
                    <tbody>
                        {recentSales.length === 0 ? (
                            <tr>
                                <td colSpan="5" style={{ textAlign: 'center', padding: '30px', color: '#7f8c8d' }}>
                                    لا توجد مبيعات بعد
                                </td>
                            </tr>
                        ) : (
                            recentSales.map(sale => (
                                <tr key={sale.id}>
                                    <td>{sale.invoice_no}</td>
                                    <td>{sale.sale_date}</td>
                                    <td>{sale.customer_name || 'عميل نقدي'}</td>
                                    <td>{formatCurrency(sale.total)}</td>
                                    <td>
                                        <span className={`status-badge ${getStatusClass(sale.status)}`}>
                                            {sale.status}
                                        </span>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Low Stock Products */}
            <div className="card">
                <div className="card-header">
                    <h2>الأصناف المنخفضة بالمخزون ({stats.low_stock_count})</h2>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>اسم الصنف</th>
                            <th>الفئة</th>
                            <th>الكمية المتاحة</th>
                            <th>الحد الأدنى</th>
                            <th>الحالة</th>
                        </tr>
                    </thead>
                    <tbody>
                        {lowStock.length === 0 ? (
                            <tr>
                                <td colSpan="5" style={{ textAlign: 'center', padding: '30px', color: '#7f8c8d' }}>
                                    جميع الأصناف متوفرة بكميات كافية
                                </td>
                            </tr>
                        ) : (
                            lowStock.map((product, index) => (
                                <tr key={index}>
                                    <td>{product.name}</td>
                                    <td>{product.category || '-'}</td>
                                    <td>{product.quantity}</td>
                                    <td>{product.min_quantity}</td>
                                    <td>
                                        <span className={`status-badge ${product.quantity === 0 ? 'danger' : 'warning'}`}>
                                            {product.status}
                                        </span>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </>
    )
}

export default Dashboard
