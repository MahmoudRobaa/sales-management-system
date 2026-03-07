import { useState, useEffect } from 'react'
import { ProductsAPI, InventoryAPI } from '../services/api'

const getErrorMessage = (error, fallback = 'حدث خطأ') => {
    const detail = error?.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) return detail.map(d => d.msg || d.message || JSON.stringify(d)).join(', ')
    return error?.message || fallback
}

function Inventory() {
    const [products, setProducts] = useState([])
    const [loading, setLoading] = useState(true)
    const [showModal, setShowModal] = useState(false)
    const [showMovementsModal, setShowMovementsModal] = useState(false)
    const [movements, setMovements] = useState([])
    const [movementsLoading, setMovementsLoading] = useState(false)
    const [selectedProduct, setSelectedProduct] = useState(null)
    const [adjustmentData, setAdjustmentData] = useState({
        adjustment_type: 'add',
        quantity: '',
        reason: '',
        notes: ''
    })

    useEffect(() => {
        loadProducts()
    }, [])

    const loadProducts = async () => {
        try {
            setLoading(true)
            const data = await ProductsAPI.getAll()
            setProducts(data)
        } catch (error) {
            console.error('Error loading products:', error)
        } finally {
            setLoading(false)
        }
    }

    const formatCurrency = (amount) => parseFloat(amount || 0).toFixed(2) + ' ج.م'

    const getStockStatus = (product) => {
        if (product.quantity === 0) return { text: 'نفذ', class: 'danger' }
        if (product.quantity <= product.min_quantity) return { text: 'منخفض', class: 'warning' }
        return { text: 'جيد', class: 'success' }
    }

    const openAdjustment = (product) => {
        setSelectedProduct(product)
        setAdjustmentData({ adjustment_type: 'add', quantity: '', reason: '', notes: '' })
        setShowModal(true)
    }

    const handleAdjustment = async (e) => {
        e.preventDefault()
        if (!adjustmentData.quantity || parseInt(adjustmentData.quantity) <= 0) {
            alert('يرجى إدخال كمية صحيحة')
            return
        }

        try {
            await InventoryAPI.adjust({
                product_id: selectedProduct.id,
                adjustment_type: adjustmentData.adjustment_type,
                quantity: parseInt(adjustmentData.quantity),
                reason: adjustmentData.reason,
                notes: adjustmentData.notes
            })
            setShowModal(false)
            loadProducts()
        } catch (error) {
            console.error('Error adjusting inventory:', error)
            alert(getErrorMessage(error, 'خطأ في تعديل المخزون'))
        }
    }

    const loadMovements = async () => {
        setMovementsLoading(true)
        try {
            const data = await InventoryAPI.getMovements()
            setMovements(data)
            setShowMovementsModal(true)
        } catch (error) {
            console.error('Error loading movements:', error)
            alert('خطأ في تحميل سجل التعديلات')
        } finally {
            setMovementsLoading(false)
        }
    }

    const formatDate = (dateStr) => {
        if (!dateStr) return '-'
        const date = new Date(dateStr)
        return date.toLocaleDateString('ar-EG', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    }

    const getMovementTypeLabel = (type) => {
        const types = {
            'purchase': 'شراء',
            'sale': 'بيع',
            'adjustment_add': 'إضافة يدوية',
            'adjustment_subtract': 'خصم يدوي',
            'adjustment_set': 'تعيين كمية'
        }
        return types[type] || type
    }

    if (loading) {
        return <div className="loading"><div className="loading-spinner"></div><span>جاري التحميل...</span></div>
    }

    return (
        <>
            <div className="page-header">
                <h1>المخازن</h1>
                <button className="btn btn-secondary" onClick={loadMovements} disabled={movementsLoading}>
                    <i className="fas fa-history"></i> {movementsLoading ? 'جاري التحميل...' : 'سجل التعديلات'}
                </button>
            </div>

            <div className="card">
                <table>
                    <thead>
                        <tr>
                            <th>اسم الصنف</th>
                            <th>الفئة</th>
                            <th>الكمية المتاحة</th>
                            <th>الحد الأدنى</th>
                            <th>سعر الشراء</th>
                            <th>قيمة المخزون</th>
                            <th>الحالة</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {products.map(product => {
                            const status = getStockStatus(product)
                            const totalValue = product.quantity * product.purchase_price
                            return (
                                <tr key={product.id}>
                                    <td>{product.name}</td>
                                    <td>{product.category || '-'}</td>
                                    <td>{product.quantity}</td>
                                    <td>{product.min_quantity}</td>
                                    <td>{formatCurrency(product.purchase_price)}</td>
                                    <td>{formatCurrency(totalValue)}</td>
                                    <td><span className={`status-badge ${status.class}`}>{status.text}</span></td>
                                    <td>
                                        <button className="btn btn-sm btn-primary" onClick={() => openAdjustment(product)}>
                                            <i className="fas fa-edit"></i> تعديل
                                        </button>
                                    </td>
                                </tr>
                            )
                        })}
                    </tbody>
                </table>
            </div>

            {showModal && selectedProduct && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>تعديل المخزون - {selectedProduct.name}</h3>
                            <button className="modal-close" onClick={() => setShowModal(false)}>&times;</button>
                        </div>
                        <form onSubmit={handleAdjustment}>
                            <div className="modal-body">
                                <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
                                    <p><strong>الكمية الحالية:</strong> {selectedProduct.quantity}</p>
                                </div>

                                <div className="form-group">
                                    <label>نوع التعديل</label>
                                    <select className="form-control" value={adjustmentData.adjustment_type} onChange={e => setAdjustmentData({ ...adjustmentData, adjustment_type: e.target.value })}>
                                        <option value="add">إضافة</option>
                                        <option value="subtract">خصم</option>
                                        <option value="set">تعيين كمية محددة</option>
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label>الكمية</label>
                                    <input type="number" min="1" className="form-control" value={adjustmentData.quantity} onChange={e => setAdjustmentData({ ...adjustmentData, quantity: e.target.value })} required />
                                </div>

                                <div className="form-group">
                                    <label>السبب</label>
                                    <select className="form-control" value={adjustmentData.reason} onChange={e => setAdjustmentData({ ...adjustmentData, reason: e.target.value })}>
                                        <option value="">اختر السبب</option>
                                        <option value="جرد">جرد</option>
                                        <option value="تالف">تالف</option>
                                        <option value="مرتجع">مرتجع</option>
                                        <option value="تصحيح">تصحيح خطأ</option>
                                        <option value="أخرى">أخرى</option>
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label>ملاحظات</label>
                                    <textarea className="form-control" rows="2" value={adjustmentData.notes} onChange={e => setAdjustmentData({ ...adjustmentData, notes: e.target.value })}></textarea>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn" onClick={() => setShowModal(false)}>إلغاء</button>
                                <button type="submit" className="btn btn-primary">تطبيق التعديل</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Inventory Movements History Modal */}
            {showMovementsModal && (
                <div className="modal-overlay" onClick={() => setShowMovementsModal(false)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '900px' }}>
                        <div className="modal-header" style={{ background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)' }}>
                            <h3><i className="fas fa-history"></i> سجل تعديلات المخزون</h3>
                            <button className="modal-close" onClick={() => setShowMovementsModal(false)}>&times;</button>
                        </div>
                        <div className="modal-body" style={{ maxHeight: '500px', overflowY: 'auto' }}>
                            {movements.length === 0 ? (
                                <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
                                    <i className="fas fa-inbox" style={{ fontSize: '3rem', marginBottom: '15px' }}></i>
                                    <p>لا توجد تعديلات مسجلة</p>
                                </div>
                            ) : (
                                <table>
                                    <thead>
                                        <tr>
                                            <th>التاريخ</th>
                                            <th>الصنف</th>
                                            <th>نوع الحركة</th>
                                            <th>الكمية قبل</th>
                                            <th>التغيير</th>
                                            <th>الكمية بعد</th>
                                            <th>السبب</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {movements.slice(0, 50).map((movement, index) => (
                                            <tr key={index}>
                                                <td style={{ whiteSpace: 'nowrap', fontSize: '0.85rem' }}>{formatDate(movement.created_at)}</td>
                                                <td>{movement.product_name || `#${movement.product_id}`}</td>
                                                <td>
                                                    <span className={`status-badge ${movement.quantity_change > 0 ? 'success' : 'warning'}`}>
                                                        {getMovementTypeLabel(movement.movement_type)}
                                                    </span>
                                                </td>
                                                <td>{movement.quantity_before}</td>
                                                <td style={{ fontWeight: '600', color: movement.quantity_change > 0 ? '#10b981' : '#ef4444' }}>
                                                    {movement.quantity_change > 0 ? '+' : ''}{movement.quantity_change}
                                                </td>
                                                <td>{movement.quantity_after}</td>
                                                <td>{movement.reason || '-'}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                        <div className="modal-footer">
                            <button type="button" className="btn" onClick={() => setShowMovementsModal(false)}>إغلاق</button>
                        </div>
                    </div>
                </div>
            )}
        </>
    )
}

export default Inventory
