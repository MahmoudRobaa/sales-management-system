import { useState, useEffect } from 'react'
import { StocktakeAPI, InvoicingAPI, BatchesAPI } from '../services/api'

function StocktakeComponent() {
    const [stocktakes, setStocktakes] = useState([])
    const [loading, setLoading] = useState(true)
    const [selectedStocktake, setSelectedStocktake] = useState(null)
    const [countForm, setCountForm] = useState({})

    useEffect(() => { loadStocktakes() }, [])

    const loadStocktakes = async () => {
        try {
            setLoading(true)
            setStocktakes(await StocktakeAPI.getAll())
        } catch (error) {
            console.error('Error loading stocktakes:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleCreate = async () => {
        try {
            const st = await StocktakeAPI.create()
            alert(`تم إنشاء جرد جديد: ${st.reference}`)
            loadStocktakes()
        } catch (error) {
            alert(error.response?.data?.detail || 'خطأ في إنشاء الجرد')
        }
    }

    const loadDetail = async (id) => {
        try {
            const data = await StocktakeAPI.getById(id)
            setSelectedStocktake(data)
            const counts = {}
            data.items?.forEach(item => {
                counts[item.id] = item.counted_quantity ?? ''
            })
            setCountForm(counts)
        } catch (error) {
            alert('خطأ في تحميل بيانات الجرد')
        }
    }

    const handleUpdateCount = async (itemId, counted) => {
        try {
            await StocktakeAPI.updateCount(selectedStocktake.id, { item_id: itemId, counted_quantity: parseInt(counted) })
            setCountForm(prev => ({ ...prev, [itemId]: counted }))
        } catch (error) {
            alert('خطأ في تحديث العدد')
        }
    }

    const handleComplete = async () => {
        if (!confirm('هل تريد إتمام الجرد وتعديل المخزون؟ هذا الإجراء لا يمكن التراجع عنه.')) return
        try {
            await StocktakeAPI.complete(selectedStocktake.id)
            alert('تم إتمام الجرد وتعديل المخزون')
            setSelectedStocktake(null)
            loadStocktakes()
        } catch (error) {
            alert(error.response?.data?.detail || 'خطأ في إتمام الجرد')
        }
    }

    const formatCurrency = (amount) => parseFloat(amount || 0).toFixed(2) + ' ج.م'
    const statusLabels = { in_progress: 'جارٍ', completed: 'مكتمل' }

    if (loading) return <div className="loading"><div className="spinner"></div></div>

    return (
        <div>
            <div className="section-header">
                <h2><i className="fas fa-clipboard-check"></i> الجرد</h2>
                <button className="btn btn-primary" onClick={handleCreate}>
                    <i className="fas fa-plus"></i> جرد جديد
                </button>
            </div>

            {!selectedStocktake ? (
                <div className="table-container">
                    <table>
                        <thead>
                            <tr><th>المرجع</th><th>الحالة</th><th>تاريخ الإنشاء</th><th>تاريخ الإكمال</th><th>الإجراءات</th></tr>
                        </thead>
                        <tbody>
                            {stocktakes.map(st => (
                                <tr key={st.id}>
                                    <td>{st.reference}</td>
                                    <td><span className={`badge badge-${st.status === 'completed' ? 'success' : 'warning'}`}>{statusLabels[st.status] || st.status}</span></td>
                                    <td>{st.created_at ? new Date(st.created_at).toLocaleDateString('ar-EG') : '-'}</td>
                                    <td>{st.completed_at ? new Date(st.completed_at).toLocaleDateString('ar-EG') : '-'}</td>
                                    <td>
                                        <button className="btn btn-sm btn-info" onClick={() => loadDetail(st.id)}>
                                            <i className="fas fa-eye"></i> عرض
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {stocktakes.length === 0 && <tr><td colSpan="5" style={{ textAlign: 'center' }}>لا يوجد جرد</td></tr>}
                        </tbody>
                    </table>
                </div>
            ) : (
                <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                        <h3>جرد: {selectedStocktake.reference}</h3>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            {selectedStocktake.status === 'in_progress' && (
                                <button className="btn btn-success" onClick={handleComplete}>
                                    <i className="fas fa-check"></i> إتمام الجرد وتعديل المخزون
                                </button>
                            )}
                            <button className="btn btn-secondary" onClick={() => setSelectedStocktake(null)}>
                                <i className="fas fa-arrow-right"></i> رجوع
                            </button>
                        </div>
                    </div>
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr><th>المنتج</th><th>الكمية بالنظام</th><th>الكمية الفعلية</th><th>الفرق</th></tr>
                            </thead>
                            <tbody>
                                {selectedStocktake.items?.map(item => {
                                    const counted = countForm[item.id]
                                    const variance = counted !== '' && counted != null ? parseInt(counted) - item.system_quantity : null
                                    return (
                                        <tr key={item.id}>
                                            <td>{item.product_name || `#${item.product_id}`}</td>
                                            <td>{item.system_quantity}</td>
                                            <td>
                                                {selectedStocktake.status === 'in_progress' ? (
                                                    <input
                                                        type="number"
                                                        min="0"
                                                        value={countForm[item.id] ?? ''}
                                                        onChange={e => setCountForm(prev => ({ ...prev, [item.id]: e.target.value }))}
                                                        onBlur={e => e.target.value !== '' && handleUpdateCount(item.id, e.target.value)}
                                                        style={{ width: '80px' }}
                                                    />
                                                ) : (
                                                    item.counted_quantity ?? '-'
                                                )}
                                            </td>
                                            <td style={{ color: variance && variance !== 0 ? (variance > 0 ? 'green' : 'red') : 'inherit', fontWeight: 'bold' }}>
                                                {variance != null ? (variance > 0 ? `+${variance}` : variance) : '-'}
                                            </td>
                                        </tr>
                                    )
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    )
}

export default StocktakeComponent
