import { useState, useEffect } from 'react'
import { ReturnsAPI, SalesAPI } from '../services/api'

function Returns() {
    const [returns, setReturns] = useState([])
    const [loading, setLoading] = useState(true)
    const [showModal, setShowModal] = useState(false)
    const [formData, setFormData] = useState({
        sale_id: '',
        refund_method: 'cash',
        reason: '',
        restock: true,
        items: []
    })
    const [saleDetails, setSaleDetails] = useState(null)
    const [searchingSale, setSearchingSale] = useState(false)

    useEffect(() => { loadReturns() }, [])

    const loadReturns = async () => {
        try {
            setLoading(true)
            const data = await ReturnsAPI.getAll()
            setReturns(data)
        } catch (error) {
            console.error('Error loading returns:', error)
        } finally {
            setLoading(false)
        }
    }

    const lookupSale = async () => {
        if (!formData.sale_id) return
        try {
            setSearchingSale(true)
            const sale = await SalesAPI.getById(parseInt(formData.sale_id))
            setSaleDetails(sale)
            setFormData(prev => ({
                ...prev,
                items: sale.items.map(item => ({
                    product_id: item.product_id,
                    product_name: item.product_name || `#${item.product_id}`,
                    quantity: 0,
                    max_quantity: item.quantity,
                    unit_price: item.unit_price,
                    reason: ''
                }))
            }))
        } catch {
            alert('فاتورة غير موجودة')
            setSaleDetails(null)
        } finally {
            setSearchingSale(false)
        }
    }

    const updateReturnItem = (index, field, value) => {
        const items = [...formData.items]
        items[index][field] = value
        setFormData(prev => ({ ...prev, items }))
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        const validItems = formData.items.filter(i => i.quantity > 0)
        if (validItems.length === 0) {
            alert('يرجى تحديد كمية مرتجعة لعنصر واحد على الأقل')
            return
        }
        try {
            await ReturnsAPI.create({
                sale_id: parseInt(formData.sale_id),
                refund_method: formData.refund_method,
                reason: formData.reason,
                restock: formData.restock,
                items: validItems.map(i => ({
                    product_id: i.product_id,
                    quantity: parseInt(i.quantity),
                    unit_price: parseFloat(i.unit_price),
                    reason: i.reason
                }))
            })
            alert('تم تسجيل المرتجع بنجاح')
            setShowModal(false)
            resetForm()
            loadReturns()
        } catch (error) {
            alert(error.response?.data?.detail || 'خطأ في تسجيل المرتجع')
        }
    }

    const handleApprove = async (id) => {
        if (!confirm('هل تريد الموافقة على هذا المرتجع؟')) return
        try {
            await ReturnsAPI.approve(id)
            loadReturns()
        } catch (error) {
            alert(error.response?.data?.detail || 'خطأ')
        }
    }

    const resetForm = () => {
        setFormData({ sale_id: '', refund_method: 'cash', reason: '', restock: true, items: [] })
        setSaleDetails(null)
    }

    const formatCurrency = (amount) => parseFloat(amount || 0).toFixed(2) + ' ج.م'
    const statusLabels = { pending: 'قيد الانتظار', approved: 'معتمد', rejected: 'مرفوض' }

    if (loading) return <div className="loading"><div className="spinner"></div></div>

    return (
        <div>
            <div className="section-header">
                <h2><i className="fas fa-undo"></i> المرتجعات</h2>
                <button className="btn btn-primary" onClick={() => { resetForm(); setShowModal(true) }}>
                    <i className="fas fa-plus"></i> مرتجع جديد
                </button>
            </div>

            <div className="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>رقم المرتجع</th>
                            <th>رقم الفاتورة</th>
                            <th>التاريخ</th>
                            <th>الإجمالي</th>
                            <th>طريقة الاسترداد</th>
                            <th>الحالة</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {returns.map(r => (
                            <tr key={r.id}>
                                <td>{r.return_no}</td>
                                <td>#{r.sale_id}</td>
                                <td>{r.return_date}</td>
                                <td>{formatCurrency(r.total)}</td>
                                <td>{r.refund_method}</td>
                                <td><span className={`badge badge-${r.status === 'approved' ? 'success' : 'warning'}`}>{statusLabels[r.status] || r.status}</span></td>
                                <td>
                                    {r.status === 'pending' && (
                                        <button className="btn btn-sm btn-success" onClick={() => handleApprove(r.id)} title="موافقة">
                                            <i className="fas fa-check"></i>
                                        </button>
                                    )}
                                </td>
                            </tr>
                        ))}
                        {returns.length === 0 && <tr><td colSpan="7" style={{ textAlign: 'center' }}>لا توجد مرتجعات</td></tr>}
                    </tbody>
                </table>
            </div>

            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: '700px' }}>
                        <div className="modal-header">
                            <h3>مرتجع بيع جديد</h3>
                            <button className="close-btn" onClick={() => setShowModal(false)}>&times;</button>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div className="form-row">
                                <div className="form-group" style={{ flex: 2 }}>
                                    <label>رقم الفاتورة</label>
                                    <div style={{ display: 'flex', gap: '8px' }}>
                                        <input type="number" value={formData.sale_id} onChange={e => setFormData(prev => ({ ...prev, sale_id: e.target.value }))} required />
                                        <button type="button" className="btn btn-secondary" onClick={lookupSale} disabled={searchingSale}>
                                            {searchingSale ? '...' : 'بحث'}
                                        </button>
                                    </div>
                                </div>
                                <div className="form-group">
                                    <label>طريقة الاسترداد</label>
                                    <select value={formData.refund_method} onChange={e => setFormData(prev => ({ ...prev, refund_method: e.target.value }))}>
                                        <option value="cash">كاش</option>
                                        <option value="credit">رصيد عميل</option>
                                    </select>
                                </div>
                            </div>

                            <div className="form-group">
                                <label>السبب</label>
                                <input type="text" value={formData.reason} onChange={e => setFormData(prev => ({ ...prev, reason: e.target.value }))} />
                            </div>

                            <div className="form-group">
                                <label>
                                    <input type="checkbox" checked={formData.restock} onChange={e => setFormData(prev => ({ ...prev, restock: e.target.checked }))} />
                                    {' '}إعادة المنتجات للمخزون
                                </label>
                            </div>

                            {formData.items.length > 0 && (
                                <table style={{ marginBottom: '16px' }}>
                                    <thead>
                                        <tr>
                                            <th>المنتج</th>
                                            <th>الكمية الأصلية</th>
                                            <th>كمية المرتجع</th>
                                            <th>السعر</th>
                                            <th>السبب</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {formData.items.map((item, i) => (
                                            <tr key={i}>
                                                <td>{item.product_name}</td>
                                                <td>{item.max_quantity}</td>
                                                <td>
                                                    <input type="number" min="0" max={item.max_quantity} value={item.quantity} onChange={e => updateReturnItem(i, 'quantity', e.target.value)} style={{ width: '70px' }} />
                                                </td>
                                                <td>{formatCurrency(item.unit_price)}</td>
                                                <td>
                                                    <input type="text" value={item.reason} onChange={e => updateReturnItem(i, 'reason', e.target.value)} placeholder="السبب" style={{ width: '120px' }} />
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}

                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>إلغاء</button>
                                <button type="submit" className="btn btn-primary" disabled={formData.items.filter(i => i.quantity > 0).length === 0}>تسجيل المرتجع</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    )
}

export default Returns
