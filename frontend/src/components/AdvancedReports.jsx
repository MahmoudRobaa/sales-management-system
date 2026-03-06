import { useState, useEffect } from 'react'
import { ReportsAdvancedAPI } from '../services/api'

function AdvancedReports() {
    const [activeTab, setActiveTab] = useState('heatmap')
    const [loading, setLoading] = useState(false)
    const [heatmapData, setHeatmapData] = useState([])
    const [deadStock, setDeadStock] = useState([])
    const [margins, setMargins] = useState([])
    const [cashierData, setCashierData] = useState([])
    const [reorderAlerts, setReorderAlerts] = useState([])

    const formatCurrency = (amount) => parseFloat(amount || 0).toFixed(2) + ' ج.م'

    const loadTab = async (tab) => {
        setActiveTab(tab)
        setLoading(true)
        try {
            switch (tab) {
                case 'heatmap':
                    setHeatmapData(await ReportsAdvancedAPI.getHourlyHeatmap(30))
                    break
                case 'deadstock':
                    setDeadStock(await ReportsAdvancedAPI.getDeadStock(90))
                    break
                case 'margins':
                    setMargins(await ReportsAdvancedAPI.getMargins())
                    break
                case 'cashier':
                    setCashierData(await ReportsAdvancedAPI.getCashierPerformance())
                    break
                case 'reorder':
                    setReorderAlerts(await ReportsAdvancedAPI.getReorderAlerts())
                    break
            }
        } catch (error) {
            console.error('Error loading report:', error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { loadTab('heatmap') }, [])

    const tabs = [
        { id: 'heatmap', label: 'خريطة المبيعات بالساعة', icon: 'fas fa-chart-area' },
        { id: 'deadstock', label: 'المخزون الراكد', icon: 'fas fa-box-open' },
        { id: 'margins', label: 'هوامش الربح', icon: 'fas fa-percentage' },
        { id: 'cashier', label: 'أداء الكاشير', icon: 'fas fa-user-tie' },
        { id: 'reorder', label: 'تنبيهات إعادة الطلب', icon: 'fas fa-exclamation-triangle' },
    ]

    const getHeatColor = (count, max) => {
        if (max === 0) return '#f0f0f0'
        const intensity = count / max
        const r = Math.round(255 - intensity * 200)
        const g = Math.round(255 - intensity * 50)
        const b = Math.round(255 - intensity * 200)
        return `rgb(${r}, ${g}, ${b})`
    }

    const maxSalesCount = Math.max(...heatmapData.map(h => h.sales_count), 1)

    return (
        <div>
            <div className="section-header">
                <h2><i className="fas fa-chart-line"></i> التقارير المتقدمة</h2>
            </div>

            <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`btn ${activeTab === tab.id ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => loadTab(tab.id)}
                    >
                        <i className={tab.icon}></i> {tab.label}
                    </button>
                ))}
            </div>

            {loading ? (
                <div className="loading"><div className="spinner"></div></div>
            ) : (
                <>
                    {/* Hourly Heatmap */}
                    {activeTab === 'heatmap' && (
                        <div className="card" style={{ padding: '20px' }}>
                            <h3>توزيع المبيعات حسب الساعة (آخر 30 يوم)</h3>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '4px', marginTop: '16px' }}>
                                {heatmapData.map(h => (
                                    <div key={h.hour} style={{
                                        padding: '12px 4px',
                                        textAlign: 'center',
                                        borderRadius: '6px',
                                        background: getHeatColor(h.sales_count, maxSalesCount),
                                        fontSize: '12px'
                                    }}>
                                        <div style={{ fontWeight: 'bold' }}>{h.hour}:00</div>
                                        <div>{h.sales_count} عملية</div>
                                        <div style={{ fontSize: '10px' }}>{formatCurrency(h.total_amount)}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Dead Stock */}
                    {activeTab === 'deadstock' && (
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr><th>الكود</th><th>المنتج</th><th>الكمية</th><th>آخر بيع</th><th>أيام بدون بيع</th></tr>
                                </thead>
                                <tbody>
                                    {deadStock.map(item => (
                                        <tr key={item.id}>
                                            <td>{item.code}</td>
                                            <td>{item.name}</td>
                                            <td>{item.quantity}</td>
                                            <td>{item.last_sale_date || 'لم يباع'}</td>
                                            <td><span className="badge badge-danger">{item.days_without_sale} يوم</span></td>
                                        </tr>
                                    ))}
                                    {deadStock.length === 0 && <tr><td colSpan="5" style={{ textAlign: 'center' }}>لا يوجد مخزون راكد</td></tr>}
                                </tbody>
                            </table>
                        </div>
                    )}

                    {/* Profit Margins */}
                    {activeTab === 'margins' && (
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr><th>الكود</th><th>المنتج</th><th>التصنيف</th><th>سعر الشراء</th><th>سعر البيع</th><th>الهامش</th><th>الهامش %</th><th>الكمية المباعة</th><th>إجمالي الربح</th></tr>
                                </thead>
                                <tbody>
                                    {margins.map(m => (
                                        <tr key={m.id}>
                                            <td>{m.code}</td>
                                            <td>{m.name}</td>
                                            <td>{m.category || '-'}</td>
                                            <td>{formatCurrency(m.purchase_price)}</td>
                                            <td>{formatCurrency(m.sale_price)}</td>
                                            <td>{formatCurrency(m.margin)}</td>
                                            <td><span className={`badge ${m.margin_percent > 20 ? 'badge-success' : m.margin_percent > 10 ? 'badge-warning' : 'badge-danger'}`}>{m.margin_percent}%</span></td>
                                            <td>{m.total_sold}</td>
                                            <td style={{ fontWeight: 'bold', color: m.total_profit > 0 ? 'green' : 'red' }}>{formatCurrency(m.total_profit)}</td>
                                        </tr>
                                    ))}
                                    {margins.length === 0 && <tr><td colSpan="9" style={{ textAlign: 'center' }}>لا توجد بيانات</td></tr>}
                                </tbody>
                            </table>
                        </div>
                    )}

                    {/* Cashier Performance */}
                    {activeTab === 'cashier' && (
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr><th>المستخدم</th><th>الاسم</th><th>عدد المبيعات</th><th>إجمالي المبيعات</th><th>متوسط الفاتورة</th><th>عدد المرتجعات</th><th>إجمالي المرتجعات</th></tr>
                                </thead>
                                <tbody>
                                    {cashierData.map(c => (
                                        <tr key={c.user_id}>
                                            <td>{c.username}</td>
                                            <td>{c.full_name}</td>
                                            <td>{c.sales_count}</td>
                                            <td>{formatCurrency(c.total_sales)}</td>
                                            <td>{formatCurrency(c.average_sale)}</td>
                                            <td>{c.returns_count}</td>
                                            <td>{formatCurrency(c.total_returns)}</td>
                                        </tr>
                                    ))}
                                    {cashierData.length === 0 && <tr><td colSpan="7" style={{ textAlign: 'center' }}>لا توجد بيانات</td></tr>}
                                </tbody>
                            </table>
                        </div>
                    )}

                    {/* Reorder Alerts */}
                    {activeTab === 'reorder' && (
                        <div>
                            <div style={{ marginBottom: '16px' }}>
                                <button className="btn btn-primary" onClick={async () => {
                                    try {
                                        const result = await ReportsAdvancedAPI.generateAutoPO()
                                        alert(`تم إنشاء ${result.drafts?.length || 0} مسودة طلب شراء (${result.total_items} صنف)`)
                                    } catch (e) {
                                        alert('خطأ في إنشاء مسودات الطلب')
                                    }
                                }}>
                                    <i className="fas fa-magic"></i> إنشاء مسودات طلب شراء تلقائي
                                </button>
                            </div>
                            <div className="table-container">
                                <table>
                                    <thead>
                                        <tr><th>الكود</th><th>المنتج</th><th>التصنيف</th><th>المورد</th><th>الكمية الحالية</th><th>الحد الأدنى</th><th>الكمية المقترحة</th></tr>
                                    </thead>
                                    <tbody>
                                        {reorderAlerts.map(item => (
                                            <tr key={item.id}>
                                                <td>{item.code}</td>
                                                <td>{item.name}</td>
                                                <td>{item.category || '-'}</td>
                                                <td>{item.supplier_name || '-'}</td>
                                                <td><span className="badge badge-danger">{item.current_quantity}</span></td>
                                                <td>{item.min_quantity}</td>
                                                <td style={{ fontWeight: 'bold' }}>{item.suggested_order}</td>
                                            </tr>
                                        ))}
                                        {reorderAlerts.length === 0 && <tr><td colSpan="7" style={{ textAlign: 'center' }}>لا توجد تنبيهات</td></tr>}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    )
}

export default AdvancedReports
