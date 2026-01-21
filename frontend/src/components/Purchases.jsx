import { useState, useEffect } from 'react'
import { PurchasesAPI, ProductsAPI, SuppliersAPI } from '../services/api'

function Purchases({ user }) {
    const [purchases, setPurchases] = useState([])
    const [products, setProducts] = useState([])
    const [suppliers, setSuppliers] = useState([])
    const [loading, setLoading] = useState(true)
    const [showModal, setShowModal] = useState(false)
    const [showDetailsModal, setShowDetailsModal] = useState(false)
    const [selectedPurchase, setSelectedPurchase] = useState(null)
    const [editingPurchase, setEditingPurchase] = useState(null)
    const [purchaseItems, setPurchaseItems] = useState([])
    const [formData, setFormData] = useState({
        supplier_id: '',
        purchase_date: new Date().toISOString().split('T')[0],
        payment_method: 'كاش',
        discount: 0,
        paid: 0,
        notes: ''
    })
    const [selectedProduct, setSelectedProduct] = useState('')
    const [quantity, setQuantity] = useState(1)
    const [unitPrice, setUnitPrice] = useState('')

    // Check if user can edit (admin or manager)
    const canEdit = user && (user.role === 'admin' || user.role === 'manager')

    useEffect(() => {
        loadData()
    }, [])

    const loadData = async () => {
        try {
            setLoading(true)
            const [purchasesData, productsData, suppliersData] = await Promise.all([
                PurchasesAPI.getAll(),
                ProductsAPI.getAll(),
                SuppliersAPI.getAll()
            ])
            setPurchases(purchasesData)
            setProducts(productsData)
            setSuppliers(suppliersData)
        } catch (error) {
            console.error('Error loading purchases:', error)
        } finally {
            setLoading(false)
        }
    }

    const formatCurrency = (amount) => parseFloat(amount || 0).toFixed(2) + ' ج.م'

    const handleAddItem = () => {
        if (!selectedProduct || quantity < 1) {
            alert('يرجى اختيار منتج وكمية صحيحة')
            return
        }
        const product = products.find(p => p.id === parseInt(selectedProduct))
        if (!product) return

        const price = unitPrice || product.purchase_price
        const total = price * quantity

        // Get supplier information from the product
        const supplier = suppliers.find(s => s.id === product.supplier_id)
        const supplierName = supplier ? supplier.name : null

        const existingIndex = purchaseItems.findIndex(item => item.product_id === product.id)
        if (existingIndex !== -1) {
            const newItems = [...purchaseItems]
            newItems[existingIndex].quantity += quantity
            newItems[existingIndex].total += total
            setPurchaseItems(newItems)
        } else {
            setPurchaseItems([...purchaseItems, {
                product_id: product.id,
                name: product.name,
                supplier_name: supplierName,
                quantity,
                unit_price: parseFloat(price),
                total
            }])
        }

        setSelectedProduct('')
        setQuantity(1)
        setUnitPrice('')
    }

    const removeItem = (index) => {
        setPurchaseItems(purchaseItems.filter((_, i) => i !== index))
    }

    const getSubtotal = () => purchaseItems.reduce((sum, item) => sum + item.total, 0)
    const getTotal = () => getSubtotal() - parseFloat(formData.discount || 0)
    const getRemaining = () => getTotal() - parseFloat(formData.paid || 0)

    // Auto-update paid amount when items or discount changes (default = full payment)
    useEffect(() => {
        if (showModal) {
            const total = getSubtotal() - parseFloat(formData.discount || 0)
            setFormData(prev => ({ ...prev, paid: total > 0 ? total : 0 }))
        }
    }, [purchaseItems, formData.discount, showModal])

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (purchaseItems.length === 0) {
            alert('يرجى إضافة أصناف للشراء')
            return
        }

        // Warning for unpaid orders
        const paidAmount = parseFloat(formData.paid) || 0
        if (paidAmount === 0) {
            if (!window.confirm('تحذير: هذا الطلب غير مدفوع بالكامل!\n\nهل تريد المتابعة بحفظ الطلب بدون دفع؟')) {
                return
            }
        }

        const purchaseData = {
            supplier_id: formData.supplier_id ? parseInt(formData.supplier_id) : null,
            purchase_date: formData.purchase_date,
            discount: parseFloat(formData.discount) || 0,
            paid: paidAmount,
            payment_method: paidAmount > 0 ? formData.payment_method : null,
            notes: formData.notes,
            items: purchaseItems.map(item => ({
                product_id: item.product_id,
                quantity: item.quantity,
                unit_price: item.unit_price
            }))
        }

        try {
            if (editingPurchase) {
                // Update existing purchase
                await PurchasesAPI.update(editingPurchase.id, purchaseData)
            } else {
                // Create new purchase
                await PurchasesAPI.create(purchaseData)
            }
            setShowModal(false)
            setPurchaseItems([])
            setEditingPurchase(null)
            setFormData({ supplier_id: '', purchase_date: new Date().toISOString().split('T')[0], payment_method: 'كاش', discount: 0, paid: 0, notes: '' })
            loadData()
        } catch (error) {
            console.error('Error saving purchase:', error)
            alert(error.response?.data?.detail || 'خطأ في حفظ العملية')
        }
    }

    const handleDelete = async (id) => {
        if (window.confirm('هل أنت متأكد من حذف هذه العملية؟')) {
            try {
                await PurchasesAPI.delete(id)
                loadData()
            } catch (error) {
                console.error('Error deleting purchase:', error)
                alert(error.response?.data?.detail || 'خطأ في حذف العملية')
            }
        }
    }

    const openModal = () => {
        setPurchaseItems([])
        setEditingPurchase(null)
        setFormData({ supplier_id: '', purchase_date: new Date().toISOString().split('T')[0], payment_method: 'كاش', discount: 0, paid: 0, notes: '' })
        setShowModal(true)
    }

    const openEditModal = async (purchase) => {
        try {
            const details = await PurchasesAPI.getById(purchase.id)
            setEditingPurchase(details)
            setFormData({
                supplier_id: details.supplier_id || '',
                purchase_date: details.purchase_date,
                payment_method: details.payment_method || 'كاش',
                discount: details.discount || 0,
                paid: details.paid || 0,
                notes: details.notes || ''
            })
            // Convert purchase items to edit format
            setPurchaseItems(details.items.map(item => ({
                product_id: item.product_id,
                name: item.product_name,
                supplier_name: item.supplier_name,
                quantity: item.quantity,
                unit_price: parseFloat(item.unit_price),
                total: parseFloat(item.total)
            })))
            setShowModal(true)
        } catch (error) {
            console.error('Error loading purchase for edit:', error)
            alert('خطأ في تحميل بيانات الفاتورة')
        }
    }

    const viewDetails = async (purchase) => {
        try {
            const details = await PurchasesAPI.getById(purchase.id)
            setSelectedPurchase(details)
            setShowDetailsModal(true)
        } catch (error) {
            console.error('Error loading purchase details:', error)
        }
    }

    const getPaymentMethodIcon = (method) => {
        if (method === 'فيزا') return 'fa-credit-card'
        if (method === 'تحويل بنكي') return 'fa-university'
        return 'fa-money-bill'
    }

    const getPaymentStatus = (purchase) => {
        const remaining = parseFloat(purchase.remaining || 0)
        const paid = parseFloat(purchase.paid || 0)
        const total = parseFloat(purchase.total || 0)

        if (remaining <= 0) return { text: 'مدفوعة بالكامل', class: 'success', icon: 'fa-check-circle' }
        if (paid > 0) return { text: `جزئي (${formatCurrency(paid)})`, class: 'warning', icon: 'fa-clock' }
        return { text: 'غير مدفوعة', class: 'danger', icon: 'fa-times-circle' }
    }

    const handlePrint = (purchase) => {
        viewDetails(purchase)
        // Print will be triggered from details modal
    }

    if (loading) {
        return <div className="loading"><div className="loading-spinner"></div><span>جاري التحميل...</span></div>
    }

    return (
        <>
            <div className="page-header">
                <h1>المشتريات</h1>
                <button className="btn btn-primary" onClick={openModal}>
                    <i className="fas fa-plus"></i> عملية شراء جديدة
                </button>
            </div>

            <div className="card">
                <table>
                    <thead>
                        <tr>
                            <th>رقم الفاتورة</th>
                            <th>التاريخ</th>
                            <th>المورد</th>
                            <th>طريقة الدفع</th>
                            <th>الإجمالي</th>
                            <th>المدفوع</th>
                            <th>المتبقي</th>
                            <th>حالة الدفع</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {purchases.length === 0 ? (
                            <tr><td colSpan="9" style={{ textAlign: 'center', padding: '30px' }}>لا توجد مشتريات</td></tr>
                        ) : purchases.map(purchase => {
                            const paymentStatus = getPaymentStatus(purchase)
                            return (
                                <tr key={purchase.id}>
                                    <td><strong>{purchase.invoice_no}</strong></td>
                                    <td>{purchase.purchase_date}</td>
                                    <td>{purchase.supplier_name || <span className="text-muted">نقدي</span>}</td>
                                    <td>
                                        {parseFloat(purchase.paid) > 0 ? (
                                            <span className="payment-type cash">
                                                <i className={`fas ${getPaymentMethodIcon(purchase.payment_method)}`}></i>
                                                {purchase.payment_method || 'كاش'}
                                            </span>
                                        ) : (
                                            <span className="text-muted">غير مدفوع</span>
                                        )}
                                    </td>
                                    <td>{formatCurrency(purchase.total)}</td>
                                    <td className="paid-amount">{formatCurrency(purchase.paid)}</td>
                                    <td className={parseFloat(purchase.remaining) > 0 ? 'remaining-amount' : ''}>
                                        {formatCurrency(purchase.remaining)}
                                    </td>
                                    <td>
                                        <span className={`status-badge ${paymentStatus.class}`}>
                                            <i className={`fas ${paymentStatus.icon}`}></i> {paymentStatus.text}
                                        </span>
                                    </td>
                                    <td>
                                        <div className="actions">
                                            <button className="action-btn view" onClick={() => viewDetails(purchase)} title="عرض التفاصيل">
                                                <i className="fas fa-eye"></i>
                                            </button>
                                            {canEdit && (
                                                <button className="action-btn edit" onClick={() => openEditModal(purchase)} title="تعديل">
                                                    <i className="fas fa-edit"></i>
                                                </button>
                                            )}
                                            <button className="action-btn print" onClick={() => handlePrint(purchase)} title="طباعة">
                                                <i className="fas fa-print"></i>
                                            </button>
                                            {canEdit && (
                                                <button className="action-btn delete" onClick={() => handleDelete(purchase.id)} title="حذف">
                                                    <i className="fas fa-trash"></i>
                                                </button>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            )
                        })}
                    </tbody>
                </table>
            </div>

            {/* Create/Edit Purchase Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content" style={{ maxWidth: '800px' }} onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>{editingPurchase ? `تعديل فاتورة ${editingPurchase.invoice_no}` : 'عملية شراء جديدة'}</h3>
                            <button className="modal-close" onClick={() => setShowModal(false)}>&times;</button>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div className="modal-body">
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>المورد</label>
                                        <select className="form-control" value={formData.supplier_id} onChange={e => setFormData({ ...formData, supplier_id: e.target.value })}>
                                            <option value="">شراء نقدي (بدون مورد)</option>
                                            {suppliers.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label>التاريخ</label>
                                        <input type="date" className="form-control" value={formData.purchase_date} onChange={e => setFormData({ ...formData, purchase_date: e.target.value })} required />
                                    </div>
                                </div>

                                {/* Payment Method - Only show when there's payment */}
                                {parseFloat(formData.paid) > 0 && (
                                    <div className="form-group">
                                        <label>طريقة الدفع</label>
                                        <select className="form-control" value={formData.payment_method} onChange={e => setFormData({ ...formData, payment_method: e.target.value })}>
                                            <option value="كاش">كاش (Cash)</option>
                                            <option value="فيزا">فيزا (Visa)</option>
                                            <option value="تحويل بنكي">تحويل بنكي (Bank Transfer)</option>
                                            <option value="أخرى">أخرى (Other)</option>
                                        </select>
                                    </div>
                                )}

                                <div className="card" style={{ marginBottom: '20px', background: '#f8f9fa', padding: '15px' }}>
                                    <h4 style={{ marginBottom: '15px' }}>إضافة صنف</h4>
                                    <div className="form-row">
                                        <div className="form-group">
                                            <label>الصنف</label>
                                            <select className="form-control" value={selectedProduct} onChange={e => {
                                                setSelectedProduct(e.target.value)
                                                const p = products.find(pr => pr.id === parseInt(e.target.value))
                                                if (p) setUnitPrice(p.purchase_price)
                                            }}>
                                                <option value="">اختر صنف</option>
                                                {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                                            </select>
                                        </div>
                                        <div className="form-group">
                                            <label>الكمية</label>
                                            <input type="number" min="1" className="form-control" value={quantity} onChange={e => setQuantity(parseInt(e.target.value) || 1)} />
                                        </div>
                                        <div className="form-group">
                                            <label>سعر الوحدة</label>
                                            <input type="number" step="0.01" className="form-control" value={unitPrice} onChange={e => setUnitPrice(e.target.value)} placeholder="سعر الشراء" />
                                        </div>
                                    </div>
                                    <button type="button" className="btn btn-success" onClick={handleAddItem}><i className="fas fa-plus"></i> إضافة للفاتورة</button>
                                </div>

                                {purchaseItems.length > 0 && (
                                    <table style={{ marginBottom: '20px' }}>
                                        <thead><tr><th>الصنف</th><th>المورد</th><th>الكمية</th><th>السعر</th><th>الإجمالي</th><th></th></tr></thead>
                                        <tbody>
                                            {purchaseItems.map((item, index) => (
                                                <tr key={index}>
                                                    <td>{item.name}</td>
                                                    <td>{item.supplier_name || <span className="text-muted">غير محدد</span>}</td>
                                                    <td>{item.quantity}</td>
                                                    <td>{formatCurrency(item.unit_price)}</td>
                                                    <td>{formatCurrency(item.total)}</td>
                                                    <td><button type="button" className="action-btn delete" onClick={() => removeItem(index)}><i className="fas fa-trash"></i></button></td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                )}

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>الخصم</label>
                                        <input type="number" step="0.01" className="form-control" value={formData.discount} onChange={e => setFormData({ ...formData, discount: e.target.value })} />
                                    </div>
                                    <div className="form-group">
                                        <label>المدفوع</label>
                                        <input type="number" step="0.01" className="form-control" value={formData.paid} onChange={e => setFormData({ ...formData, paid: e.target.value })} />
                                    </div>
                                </div>

                                <div style={{ background: '#e8f4fc', padding: '15px', borderRadius: '8px', marginTop: '15px' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}><span>الإجمالي الفرعي:</span><strong>{formatCurrency(getSubtotal())}</strong></div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}><span>الصافي:</span><strong>{formatCurrency(getTotal())}</strong></div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>المتبقي:</span><strong style={{ color: getRemaining() > 0 ? '#e74c3c' : '#27ae60' }}>{formatCurrency(getRemaining())}</strong></div>
                                </div>

                                <div className="form-group" style={{ marginTop: '15px' }}>
                                    <label>ملاحظات</label>
                                    <textarea className="form-control" rows="2" value={formData.notes} onChange={e => setFormData({ ...formData, notes: e.target.value })}></textarea>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn" onClick={() => setShowModal(false)}>إلغاء</button>
                                <button type="submit" className="btn btn-primary" disabled={purchaseItems.length === 0}>حفظ الفاتورة</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* View Details Modal */}
            {showDetailsModal && selectedPurchase && (
                <div className="modal-overlay" onClick={() => setShowDetailsModal(false)}>
                    <div className="modal-content receipt-modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>تفاصيل فاتورة الشراء</h3>
                            <button className="modal-close" onClick={() => setShowDetailsModal(false)}>&times;</button>
                        </div>
                        <div className="modal-body receipt-content" id="receipt-content">
                            <div className="receipt-header">
                                <h2>محل الحاسوب والأدوات الكهربائية</h2>
                                <p>فاتورة شراء</p>
                            </div>

                            <div className="receipt-info">
                                <div className="info-row">
                                    <span>رقم الفاتورة:</span>
                                    <strong>{selectedPurchase.invoice_no}</strong>
                                </div>
                                <div className="info-row">
                                    <span>التاريخ:</span>
                                    <strong>{selectedPurchase.purchase_date}</strong>
                                </div>
                                <div className="info-row">
                                    <span>المورد:</span>
                                    <strong>{selectedPurchase.supplier_name || 'شراء نقدي'}</strong>
                                </div>
                                <div className="info-row">
                                    <span>طريقة الدفع:</span>
                                    <strong>{parseFloat(selectedPurchase.paid) > 0 ? (selectedPurchase.payment_method || 'كاش') : 'غير مدفوع'}</strong>
                                </div>
                            </div>

                            <table className="receipt-items">
                                <thead>
                                    <tr>
                                        <th>الصنف</th>
                                        <th>المورد</th>
                                        <th>الكمية</th>
                                        <th>السعر</th>
                                        <th>الإجمالي</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {selectedPurchase.items?.map((item, index) => (
                                        <tr key={index}>
                                            <td>{item.product_name}</td>
                                            <td>{item.supplier_name || <span className="text-muted">غير محدد</span>}</td>
                                            <td>{item.quantity}</td>
                                            <td>{formatCurrency(item.unit_price)}</td>
                                            <td>{formatCurrency(item.total)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>

                            <div className="receipt-totals">
                                <div className="total-row">
                                    <span>المجموع الفرعي:</span>
                                    <span>{formatCurrency(selectedPurchase.subtotal)}</span>
                                </div>
                                {parseFloat(selectedPurchase.discount) > 0 && (
                                    <div className="total-row discount">
                                        <span>الخصم:</span>
                                        <span>- {formatCurrency(selectedPurchase.discount)}</span>
                                    </div>
                                )}
                                <div className="total-row grand-total">
                                    <span>الإجمالي:</span>
                                    <span>{formatCurrency(selectedPurchase.total)}</span>
                                </div>
                                <hr />
                                <div className="total-row paid">
                                    <span>المدفوع:</span>
                                    <span className="success-text">{formatCurrency(selectedPurchase.paid)}</span>
                                </div>
                                <div className="total-row remaining">
                                    <span>المتبقي:</span>
                                    <span className={parseFloat(selectedPurchase.remaining) > 0 ? 'danger-text' : 'success-text'}>
                                        {formatCurrency(selectedPurchase.remaining)}
                                    </span>
                                </div>
                            </div>

                            {selectedPurchase.notes && (
                                <div className="receipt-notes">
                                    <strong>ملاحظات:</strong> {selectedPurchase.notes}
                                </div>
                            )}
                        </div>
                        <div className="modal-footer">
                            <button type="button" className="btn" onClick={() => setShowDetailsModal(false)}>إغلاق</button>
                            <button type="button" className="btn btn-primary" onClick={() => window.print()}>
                                <i className="fas fa-print"></i> طباعة
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    )
}

export default Purchases
