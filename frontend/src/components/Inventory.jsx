import { useState, useEffect } from 'react'
import { ProductsAPI, InventoryAPI } from '../services/api'

function Inventory() {
    const [products, setProducts] = useState([])
    const [loading, setLoading] = useState(true)
    const [showModal, setShowModal] = useState(false)
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
            alert(error.response?.data?.detail || 'خطأ في تعديل المخزون')
        }
    }

    if (loading) {
        return <div className="loading"><div className="loading-spinner"></div><span>جاري التحميل...</span></div>
    }

    return (
        <>
            <div className="page-header">
                <h1>المخازن</h1>
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
        </>
    )
}

export default Inventory
