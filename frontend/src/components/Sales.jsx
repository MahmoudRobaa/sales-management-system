import { useState, useEffect } from 'react'
import { SalesAPI, ProductsAPI, CustomersAPI } from '../services/api'

function Sales({ user }) {
    const [sales, setSales] = useState([])
    const [products, setProducts] = useState([])
    const [customers, setCustomers] = useState([])
    const [loading, setLoading] = useState(true)
    const [showModal, setShowModal] = useState(false)
    const [showDetailsModal, setShowDetailsModal] = useState(false)
    const [selectedSale, setSelectedSale] = useState(null)
    const [editingSale, setEditingSale] = useState(null)
    const [saleItems, setSaleItems] = useState([])
    const [formData, setFormData] = useState({
        customer_id: '',
        sale_date: new Date().toISOString().split('T')[0],
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
            const [salesData, productsData, customersData] = await Promise.all([
                SalesAPI.getAll(),
                ProductsAPI.getAll(),
                CustomersAPI.getAll()
            ])
            setSales(salesData)
            setProducts(productsData)
            setCustomers(customersData)
        } catch (error) {
            console.error('Error loading sales:', error)
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

        if (quantity > product.quantity) {
            alert(`الكمية المطلوبة غير متاحة. المتاح: ${product.quantity}`)
            return
        }

        const price = unitPrice || product.sale_price
        const total = price * quantity

        const existingIndex = saleItems.findIndex(item => item.product_id === product.id)
        if (existingIndex !== -1) {
            const newItems = [...saleItems]
            newItems[existingIndex].quantity += quantity
            newItems[existingIndex].total += total
            setSaleItems(newItems)
        } else {
            setSaleItems([...saleItems, {
                product_id: product.id,
                name: product.name,
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
        setSaleItems(saleItems.filter((_, i) => i !== index))
    }

    const getSubtotal = () => saleItems.reduce((sum, item) => sum + item.total, 0)
    const getTotal = () => getSubtotal() - parseFloat(formData.discount || 0)
    const getRemaining = () => getTotal() - parseFloat(formData.paid || 0)

    // Auto-update paid amount when items or discount changes (default = full payment)
    useEffect(() => {
        if (showModal) {
            const total = getSubtotal() - parseFloat(formData.discount || 0)
            setFormData(prev => ({ ...prev, paid: total > 0 ? total : 0 }))
        }
    }, [saleItems, formData.discount, showModal])

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (saleItems.length === 0) {
            alert('يرجى إضافة أصناف للبيع')
            return
        }

        // Warning for unpaid orders
        const paidAmount = parseFloat(formData.paid) || 0
        if (paidAmount === 0) {
            if (!window.confirm('تحذير: هذا الطلب غير مدفوع بالكامل!\n\nهل تريد المتابعة بحفظ الطلب بدون دفع؟')) {
                return
            }
        }

        const saleData = {
            customer_id: formData.customer_id ? parseInt(formData.customer_id) : null,
            sale_date: formData.sale_date,
            discount: parseFloat(formData.discount) || 0,
            paid: paidAmount,
            payment_method: paidAmount > 0 ? formData.payment_method : null,
            notes: formData.notes,
            items: saleItems.map(item => ({
                product_id: item.product_id,
                quantity: item.quantity,
                unit_price: item.unit_price
            }))
        }

        try {
            if (editingSale) {
                // Update existing sale
                await SalesAPI.update(editingSale.id, saleData)
            } else {
                // Create new sale
                await SalesAPI.create(saleData)
            }
            setShowModal(false)
            setSaleItems([])
            setEditingSale(null)
            setFormData({ customer_id: '', sale_date: new Date().toISOString().split('T')[0], payment_method: 'كاش', discount: 0, paid: 0, notes: '' })
            loadData()
        } catch (error) {
            console.error('Error saving sale:', error)
            alert(error.response?.data?.detail || 'خطأ في حفظ العملية')
        }
    }

    const handleDelete = async (id) => {
        if (window.confirm('هل أنت متأكد من حذف هذه العملية؟')) {
            try {
                await SalesAPI.delete(id)
                loadData()
            } catch (error) {
                console.error('Error deleting sale:', error)
            }
        }
    }

    const openModal = () => {
        setSaleItems([])
        setEditingSale(null)
        setFormData({ customer_id: '', sale_date: new Date().toISOString().split('T')[0], payment_method: 'كاش', discount: 0, paid: 0, notes: '' })
        setShowModal(true)
    }

    const openEditModal = async (sale) => {
        try {
            const details = await SalesAPI.getById(sale.id)
            setEditingSale(details)
            setFormData({
                customer_id: details.customer_id || '',
                sale_date: details.sale_date,
                payment_method: details.payment_method || 'كاش',
                discount: details.discount || 0,
                paid: details.paid || 0,
                notes: details.notes || ''
            })
            // Convert sale items to edit format
            setSaleItems(details.items.map(item => ({
                product_id: item.product_id,
                name: item.product_name,
                quantity: item.quantity,
                unit_price: parseFloat(item.unit_price),
                total: parseFloat(item.total)
            })))
            setShowModal(true)
        } catch (error) {
            console.error('Error loading sale for edit:', error)
            alert('خطأ في تحميل بيانات الفاتورة')
        }
    }

    const viewDetails = async (sale) => {
        try {
            const details = await SalesAPI.getById(sale.id)
            setSelectedSale(details)
            setShowDetailsModal(true)
        } catch (error) {
            console.error('Error loading sale details:', error)
        }
    }

    const getPaymentMethodIcon = (method) => {
        if (method === 'فيزا') return 'fa-credit-card'
        if (method === 'تحويل بنكي') return 'fa-university'
        return 'fa-money-bill'
    }

    const getPaymentStatus = (sale) => {
        const remaining = parseFloat(sale.remaining || 0)
        const paid = parseFloat(sale.paid || 0)

        if (remaining <= 0) return { text: 'مدفوعة بالكامل', class: 'success', icon: 'fa-check-circle' }
        if (paid > 0) return { text: `جزئي (${formatCurrency(paid)})`, class: 'warning', icon: 'fa-clock' }
        return { text: 'غير مدفوعة', class: 'danger', icon: 'fa-times-circle' }
    }

    if (loading) {
        return <div className="loading"><div className="loading-spinner"></div><span>جاري التحميل...</span></div>
    }

    return (
        <>
            <div className="page-header">
                <h1>المبيعات</h1>
                <button className="btn btn-primary" onClick={openModal}>
                    <i className="fas fa-plus"></i> عملية بيع جديدة
                </button>
            </div>

            <div className="card">
                <table>
                    <thead>
                        <tr>
                            <th>رقم الفاتورة</th>
                            <th>التاريخ</th>
                            <th>العميل</th>
                            <th>طريقة الدفع</th>
                            <th>الإجمالي</th>
                            <th>المدفوع</th>
                            <th>المتبقي</th>
                            <th>حالة الدفع</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sales.length === 0 ? (
                            <tr><td colSpan="9" style={{ textAlign: 'center', padding: '30px' }}>لا توجد مبيعات</td></tr>
                        ) : sales.map(sale => {
                            const paymentStatus = getPaymentStatus(sale)
                            return (
                                <tr key={sale.id}>
                                    <td><strong>{sale.invoice_no}</strong></td>
                                    <td>{sale.sale_date}</td>
                                    <td>{sale.customer_name || <span className="text-muted">عميل نقدي</span>}</td>
                                    <td>
                                        {parseFloat(sale.paid) > 0 ? (
                                            <span className="payment-type cash">
                                                <i className={`fas ${getPaymentMethodIcon(sale.payment_method)}`}></i>
                                                {sale.payment_method || 'كاش'}
                                            </span>
                                        ) : (
                                            <span className="text-muted">غير مدفوع</span>
                                        )}
                                    </td>
                                    <td>{formatCurrency(sale.total)}</td>
                                    <td className="paid-amount">{formatCurrency(sale.paid)}</td>
                                    <td className={parseFloat(sale.remaining) > 0 ? 'remaining-amount' : ''}>
                                        {formatCurrency(sale.remaining)}
                                    </td>
                                    <td>
                                        <span className={`status-badge ${paymentStatus.class}`}>
                                            <i className={`fas ${paymentStatus.icon}`}></i> {paymentStatus.text}
                                        </span>
                                    </td>
                                    <td>
                                        <div className="actions">
                                            <button className="action-btn view" onClick={() => viewDetails(sale)} title="عرض التفاصيل">
                                                <i className="fas fa-eye"></i>
                                            </button>
                                            {canEdit && (
                                                <button className="action-btn edit" onClick={() => openEditModal(sale)} title="تعديل">
                                                    <i className="fas fa-edit"></i>
                                                </button>
                                            )}
                                            <button className="action-btn print" onClick={() => viewDetails(sale)} title="طباعة">
                                                <i className="fas fa-print"></i>
                                            </button>
                                            {canEdit && (
                                                <button className="action-btn delete" onClick={() => handleDelete(sale.id)} title="حذف">
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

            {/* Create/Edit Sale Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content" style={{ maxWidth: '800px' }} onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>{editingSale ? `تعديل فاتورة ${editingSale.invoice_no}` : 'عملية بيع جديدة'}</h3>
                            <button className="modal-close" onClick={() => setShowModal(false)}>&times;</button>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div className="modal-body">
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>العميل</label>
                                        <select className="form-control" value={formData.customer_id} onChange={e => setFormData({ ...formData, customer_id: e.target.value })}>
                                            <option value="">عميل نقدي</option>
                                            {customers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label>التاريخ</label>
                                        <input type="date" className="form-control" value={formData.sale_date} onChange={e => setFormData({ ...formData, sale_date: e.target.value })} required />
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
                                                if (p) setUnitPrice(p.sale_price)
                                            }}>
                                                <option value="">اختر صنف</option>
                                                {products.filter(p => p.quantity > 0).map(p => <option key={p.id} value={p.id}>{p.name} ({p.quantity} متاح)</option>)}
                                            </select>
                                        </div>
                                        <div className="form-group">
                                            <label>الكمية</label>
                                            <input type="number" min="1" className="form-control" value={quantity} onChange={e => setQuantity(parseInt(e.target.value) || 1)} />
                                        </div>
                                        <div className="form-group">
                                            <label>السعر</label>
                                            <input type="number" step="0.01" className="form-control" value={unitPrice} onChange={e => setUnitPrice(e.target.value)} placeholder="سعر البيع" />
                                        </div>
                                    </div>
                                    <button type="button" className="btn btn-success" onClick={handleAddItem}><i className="fas fa-plus"></i> إضافة</button>
                                </div>

                                {saleItems.length > 0 && (
                                    <table style={{ marginBottom: '20px' }}>
                                        <thead><tr><th>الصنف</th><th>الكمية</th><th>السعر</th><th>الإجمالي</th><th></th></tr></thead>
                                        <tbody>
                                            {saleItems.map((item, index) => (
                                                <tr key={index}>
                                                    <td>{item.name}</td>
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
                                <button type="submit" className="btn btn-primary" disabled={saleItems.length === 0}>حفظ الفاتورة</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* View Details Modal */}
            {showDetailsModal && selectedSale && (
                <div className="modal-overlay" onClick={() => setShowDetailsModal(false)}>
                    <div className="modal-content receipt-modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>تفاصيل فاتورة البيع</h3>
                            <button className="modal-close" onClick={() => setShowDetailsModal(false)}>&times;</button>
                        </div>
                        <div className="modal-body receipt-content" id="receipt-content">
                            <div className="receipt-header">
                                <h2>محل الحاسوب والأدوات الكهربائية</h2>
                                <p>فاتورة مبيعات</p>
                            </div>

                            <div className="receipt-info">
                                <div className="info-row">
                                    <span>رقم الفاتورة:</span>
                                    <strong>{selectedSale.invoice_no}</strong>
                                </div>
                                <div className="info-row">
                                    <span>التاريخ:</span>
                                    <strong>{selectedSale.sale_date}</strong>
                                </div>
                                <div className="info-row">
                                    <span>العميل:</span>
                                    <strong>{selectedSale.customer_name || 'عميل نقدي'}</strong>
                                </div>
                                <div className="info-row">
                                    <span>طريقة الدفع:</span>
                                    <strong>{parseFloat(selectedSale.paid) > 0 ? (selectedSale.payment_method || 'كاش') : 'غير مدفوع'}</strong>
                                </div>
                            </div>

                            <table className="receipt-items">
                                <thead>
                                    <tr>
                                        <th>الصنف</th>
                                        <th>الكمية</th>
                                        <th>السعر</th>
                                        <th>الإجمالي</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {selectedSale.items?.map((item, index) => (
                                        <tr key={index}>
                                            <td>{item.product_name}</td>
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
                                    <span>{formatCurrency(selectedSale.subtotal)}</span>
                                </div>
                                {parseFloat(selectedSale.discount) > 0 && (
                                    <div className="total-row discount">
                                        <span>الخصم:</span>
                                        <span>- {formatCurrency(selectedSale.discount)}</span>
                                    </div>
                                )}
                                <div className="total-row grand-total">
                                    <span>الإجمالي:</span>
                                    <span>{formatCurrency(selectedSale.total)}</span>
                                </div>
                                <hr />
                                <div className="total-row paid">
                                    <span>المدفوع:</span>
                                    <span className="success-text">{formatCurrency(selectedSale.paid)}</span>
                                </div>
                                <div className="total-row remaining">
                                    <span>المتبقي:</span>
                                    <span className={parseFloat(selectedSale.remaining) > 0 ? 'danger-text' : 'success-text'}>
                                        {formatCurrency(selectedSale.remaining)}
                                    </span>
                                </div>
                            </div>

                            {selectedSale.notes && (
                                <div className="receipt-notes">
                                    <strong>ملاحظات:</strong> {selectedSale.notes}
                                </div>
                            )}

                            <div className="receipt-footer">
                                <p>شكراً لتعاملكم معنا!</p>
                            </div>
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

export default Sales
