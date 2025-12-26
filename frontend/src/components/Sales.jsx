import { useState, useEffect } from 'react'
import { SalesAPI, ProductsAPI, CustomersAPI } from '../services/api'

function Sales() {
    const [sales, setSales] = useState([])
    const [products, setProducts] = useState([])
    const [customers, setCustomers] = useState([])
    const [loading, setLoading] = useState(true)
    const [showModal, setShowModal] = useState(false)
    const [saleItems, setSaleItems] = useState([])
    const [formData, setFormData] = useState({
        customer_id: '',
        sale_date: new Date().toISOString().split('T')[0],
        discount: 0,
        paid: 0,
        notes: ''
    })
    const [selectedProduct, setSelectedProduct] = useState('')
    const [quantity, setQuantity] = useState(1)
    const [unitPrice, setUnitPrice] = useState('')

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

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (saleItems.length === 0) {
            alert('يرجى إضافة أصناف للبيع')
            return
        }

        try {
            await SalesAPI.create({
                customer_id: formData.customer_id ? parseInt(formData.customer_id) : null,
                sale_date: formData.sale_date,
                discount: parseFloat(formData.discount) || 0,
                paid: parseFloat(formData.paid) || 0,
                notes: formData.notes,
                items: saleItems.map(item => ({
                    product_id: item.product_id,
                    quantity: item.quantity,
                    unit_price: item.unit_price
                }))
            })
            setShowModal(false)
            setSaleItems([])
            setFormData({ customer_id: '', sale_date: new Date().toISOString().split('T')[0], discount: 0, paid: 0, notes: '' })
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
        setFormData({ customer_id: '', sale_date: new Date().toISOString().split('T')[0], discount: 0, paid: 0, notes: '' })
        setShowModal(true)
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
                            <th>الإجمالي</th>
                            <th>المدفوع</th>
                            <th>المتبقي</th>
                            <th>الحالة</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sales.length === 0 ? (
                            <tr><td colSpan="8" style={{ textAlign: 'center', padding: '30px' }}>لا توجد مبيعات</td></tr>
                        ) : sales.map(sale => (
                            <tr key={sale.id}>
                                <td>{sale.invoice_no}</td>
                                <td>{sale.sale_date}</td>
                                <td>{sale.customer_name || 'عميل نقدي'}</td>
                                <td>{formatCurrency(sale.total)}</td>
                                <td>{formatCurrency(sale.paid)}</td>
                                <td>{formatCurrency(sale.remaining)}</td>
                                <td><span className={`status-badge ${sale.status === 'مدفوعة' ? 'success' : sale.status === 'جزئي' ? 'info' : 'danger'}`}>{sale.status}</span></td>
                                <td>
                                    <div className="actions">
                                        <button className="action-btn delete" onClick={() => handleDelete(sale.id)}>
                                            <i className="fas fa-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content" style={{ maxWidth: '800px' }} onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>عملية بيع جديدة</h3>
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

                                <div className="card" style={{ marginBottom: '20px', background: '#f8f9fa' }}>
                                    <h4 style={{ marginBottom: '15px' }}>إضافة صنف</h4>
                                    <div className="form-row">
                                        <div className="form-group">
                                            <label>الصنف</label>
                                            <select className="form-control" value={selectedProduct} onChange={e => { setSelectedProduct(e.target.value); const p = products.find(pr => pr.id === parseInt(e.target.value)); if (p) setUnitPrice(p.sale_price) }}>
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
        </>
    )
}

export default Sales
