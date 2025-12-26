import { useState, useEffect } from 'react'
import { CustomersAPI } from '../services/api'

function Customers() {
    const [customers, setCustomers] = useState([])
    const [loading, setLoading] = useState(true)
    const [showModal, setShowModal] = useState(false)
    const [editingCustomer, setEditingCustomer] = useState(null)
    const [searchTerm, setSearchTerm] = useState('')
    const [formData, setFormData] = useState({
        code: '',
        name: '',
        phone: '',
        email: '',
        address: ''
    })

    useEffect(() => {
        loadCustomers()
    }, [])

    const loadCustomers = async () => {
        try {
            setLoading(true)
            const data = await CustomersAPI.getAll()
            setCustomers(data)
        } catch (error) {
            console.error('Error loading customers:', error)
        } finally {
            setLoading(false)
        }
    }

    const formatCurrency = (amount) => parseFloat(amount || 0).toFixed(2) + ' ج.م'

    const handleAdd = () => {
        setEditingCustomer(null)
        setFormData({
            code: `CUST${String(customers.length + 1).padStart(3, '0')}`,
            name: '',
            phone: '',
            email: '',
            address: ''
        })
        setShowModal(true)
    }

    const handleEdit = async (id) => {
        try {
            const customer = await CustomersAPI.getById(id)
            setEditingCustomer(customer)
            setFormData({
                code: customer.code,
                name: customer.name,
                phone: customer.phone || '',
                email: customer.email || '',
                address: customer.address || ''
            })
            setShowModal(true)
        } catch (error) {
            console.error('Error loading customer:', error)
            alert('خطأ في تحميل بيانات العميل')
        }
    }

    const handleDelete = async (id) => {
        if (window.confirm('هل أنت متأكد من حذف هذا العميل؟')) {
            try {
                await CustomersAPI.delete(id)
                loadCustomers()
            } catch (error) {
                console.error('Error deleting customer:', error)
                alert('خطأ في حذف العميل')
            }
        }
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
            if (editingCustomer) {
                await CustomersAPI.update(editingCustomer.id, formData)
            } else {
                await CustomersAPI.create(formData)
            }
            setShowModal(false)
            loadCustomers()
        } catch (error) {
            console.error('Error saving customer:', error)
            alert(error.response?.data?.detail || 'خطأ في حفظ العميل')
        }
    }

    const filteredCustomers = customers.filter(c =>
        c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (c.phone && c.phone.includes(searchTerm))
    )

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
                <h1>العملاء</h1>
                <button className="btn btn-primary" onClick={handleAdd}>
                    <i className="fas fa-plus"></i> إضافة عميل جديد
                </button>
            </div>

            <div className="card">
                <div className="search-box">
                    <input
                        type="text"
                        placeholder="بحث عن عميل..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                    <i className="fas fa-search"></i>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>كود العميل</th>
                            <th>اسم العميل</th>
                            <th>الهاتف</th>
                            <th>البريد الإلكتروني</th>
                            <th>إجمالي المشتريات</th>
                            <th>الرصيد</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredCustomers.map(customer => (
                            <tr key={customer.id}>
                                <td>{customer.code}</td>
                                <td>{customer.name}</td>
                                <td>{customer.phone || '-'}</td>
                                <td>{customer.email || '-'}</td>
                                <td>{formatCurrency(customer.total_purchases)}</td>
                                <td>{formatCurrency(customer.balance)}</td>
                                <td>
                                    <div className="actions">
                                        <button className="action-btn edit" onClick={() => handleEdit(customer.id)}>
                                            <i className="fas fa-edit"></i>
                                        </button>
                                        <button className="action-btn delete" onClick={() => handleDelete(customer.id)}>
                                            <i className="fas fa-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>{editingCustomer ? 'تعديل العميل' : 'إضافة عميل جديد'}</h3>
                            <button className="modal-close" onClick={() => setShowModal(false)}>&times;</button>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div className="modal-body">
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>كود العميل</label>
                                        <input
                                            type="text"
                                            className="form-control"
                                            value={formData.code}
                                            onChange={e => setFormData({ ...formData, code: e.target.value })}
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>اسم العميل</label>
                                        <input
                                            type="text"
                                            className="form-control"
                                            value={formData.name}
                                            onChange={e => setFormData({ ...formData, name: e.target.value })}
                                            required
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>الهاتف</label>
                                        <input
                                            type="text"
                                            className="form-control"
                                            value={formData.phone}
                                            onChange={e => setFormData({ ...formData, phone: e.target.value })}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>البريد الإلكتروني</label>
                                        <input
                                            type="email"
                                            className="form-control"
                                            value={formData.email}
                                            onChange={e => setFormData({ ...formData, email: e.target.value })}
                                        />
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label>العنوان</label>
                                    <textarea
                                        className="form-control"
                                        rows="2"
                                        value={formData.address}
                                        onChange={e => setFormData({ ...formData, address: e.target.value })}
                                    ></textarea>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn" onClick={() => setShowModal(false)}>إلغاء</button>
                                <button type="submit" className="btn btn-primary">حفظ</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </>
    )
}

export default Customers
