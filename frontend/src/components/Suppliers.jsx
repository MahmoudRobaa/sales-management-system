import { useState, useEffect } from 'react'
import { SuppliersAPI } from '../services/api'

function Suppliers() {
    const [suppliers, setSuppliers] = useState([])
    const [loading, setLoading] = useState(true)
    const [showModal, setShowModal] = useState(false)
    const [editingSupplier, setEditingSupplier] = useState(null)
    const [searchTerm, setSearchTerm] = useState('')
    const [formData, setFormData] = useState({
        code: '',
        name: '',
        phone: '',
        email: '',
        address: ''
    })

    useEffect(() => {
        loadSuppliers()
    }, [])

    const loadSuppliers = async () => {
        try {
            setLoading(true)
            const data = await SuppliersAPI.getAll()
            setSuppliers(data)
        } catch (error) {
            console.error('Error loading suppliers:', error)
        } finally {
            setLoading(false)
        }
    }

    const formatCurrency = (amount) => parseFloat(amount || 0).toFixed(2) + ' ج.م'

    const handleAdd = () => {
        setEditingSupplier(null)
        setFormData({
            code: `SUPP${String(suppliers.length + 1).padStart(3, '0')}`,
            name: '',
            phone: '',
            email: '',
            address: ''
        })
        setShowModal(true)
    }

    const handleEdit = async (id) => {
        try {
            const supplier = await SuppliersAPI.getById(id)
            setEditingSupplier(supplier)
            setFormData({
                code: supplier.code,
                name: supplier.name,
                phone: supplier.phone || '',
                email: supplier.email || '',
                address: supplier.address || ''
            })
            setShowModal(true)
        } catch (error) {
            console.error('Error loading supplier:', error)
        }
    }

    const handleDelete = async (id) => {
        if (window.confirm('هل أنت متأكد من حذف هذا المورد؟')) {
            try {
                await SuppliersAPI.delete(id)
                loadSuppliers()
            } catch (error) {
                console.error('Error deleting supplier:', error)
            }
        }
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
            if (editingSupplier) {
                await SuppliersAPI.update(editingSupplier.id, formData)
            } else {
                await SuppliersAPI.create(formData)
            }
            setShowModal(false)
            loadSuppliers()
        } catch (error) {
            console.error('Error saving supplier:', error)
            alert(error.response?.data?.detail || 'خطأ في حفظ المورد')
        }
    }

    const filteredSuppliers = suppliers.filter(s =>
        s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.code.toLowerCase().includes(searchTerm.toLowerCase())
    )

    if (loading) {
        return <div className="loading"><div className="loading-spinner"></div><span>جاري التحميل...</span></div>
    }

    return (
        <>
            <div className="page-header">
                <h1>الموردين</h1>
                <button className="btn btn-primary" onClick={handleAdd}>
                    <i className="fas fa-plus"></i> إضافة مورد جديد
                </button>
            </div>

            <div className="card">
                <div className="search-box">
                    <input type="text" placeholder="بحث عن مورد..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
                    <i className="fas fa-search"></i>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>كود المورد</th>
                            <th>اسم المورد</th>
                            <th>الهاتف</th>
                            <th>البريد الإلكتروني</th>
                            <th>العنوان</th>
                            <th>إجمالي المشتريات</th>
                            <th>الرصيد</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredSuppliers.map(supplier => (
                            <tr key={supplier.id}>
                                <td>{supplier.code}</td>
                                <td>{supplier.name}</td>
                                <td>{supplier.phone || '-'}</td>
                                <td>{supplier.email || '-'}</td>
                                <td>{supplier.address || '-'}</td>
                                <td>{formatCurrency(supplier.total_purchases)}</td>
                                <td>{formatCurrency(supplier.balance)}</td>
                                <td>
                                    <div className="actions">
                                        <button className="action-btn edit" onClick={() => handleEdit(supplier.id)}>
                                            <i className="fas fa-edit"></i>
                                        </button>
                                        <button className="action-btn delete" onClick={() => handleDelete(supplier.id)}>
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
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>{editingSupplier ? 'تعديل المورد' : 'إضافة مورد جديد'}</h3>
                            <button className="modal-close" onClick={() => setShowModal(false)}>&times;</button>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div className="modal-body">
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>كود المورد</label>
                                        <input type="text" className="form-control" value={formData.code} onChange={e => setFormData({ ...formData, code: e.target.value })} required />
                                    </div>
                                    <div className="form-group">
                                        <label>اسم المورد</label>
                                        <input type="text" className="form-control" value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} required />
                                    </div>
                                </div>
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>الهاتف</label>
                                        <input type="text" className="form-control" value={formData.phone} onChange={e => setFormData({ ...formData, phone: e.target.value })} />
                                    </div>
                                    <div className="form-group">
                                        <label>البريد الإلكتروني</label>
                                        <input type="email" className="form-control" value={formData.email} onChange={e => setFormData({ ...formData, email: e.target.value })} />
                                    </div>
                                </div>
                                <div className="form-group">
                                    <label>العنوان</label>
                                    <textarea className="form-control" rows="2" value={formData.address} onChange={e => setFormData({ ...formData, address: e.target.value })}></textarea>
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

export default Suppliers
