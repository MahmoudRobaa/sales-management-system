import { useState, useEffect } from 'react'
import { ProductsAPI, CategoriesAPI, SuppliersAPI } from '../services/api'

function Products() {
    const [products, setProducts] = useState([])
    const [categories, setCategories] = useState([])
    const [suppliers, setSuppliers] = useState([])
    const [loading, setLoading] = useState(true)
    const [showModal, setShowModal] = useState(false)
    const [editingProduct, setEditingProduct] = useState(null)
    const [searchTerm, setSearchTerm] = useState('')
    const [formData, setFormData] = useState({
        code: '',
        name: '',
        category_id: '',
        supplier_id: '',
        purchase_price: '',
        sale_price: '',
        quantity: '',
        min_quantity: '5',
        description: ''
    })

    useEffect(() => {
        loadData()
    }, [])

    const loadData = async () => {
        try {
            setLoading(true)
            const [productsData, categoriesData, suppliersData] = await Promise.all([
                ProductsAPI.getAll(),
                CategoriesAPI.getAll(),
                SuppliersAPI.getAll()
            ])
            setProducts(productsData)
            setCategories(categoriesData)
            setSuppliers(suppliersData)
        } catch (error) {
            console.error('Error loading products:', error)
        } finally {
            setLoading(false)
        }
    }

    const formatCurrency = (amount) => parseFloat(amount || 0).toFixed(2) + ' ج.م'

    const handleAdd = () => {
        setEditingProduct(null)
        setFormData({
            code: `PROD${String(products.length + 1).padStart(3, '0')}`,
            name: '',
            category_id: '',
            supplier_id: '',
            purchase_price: '',
            sale_price: '',
            quantity: '',
            min_quantity: '5',
            description: ''
        })
        setShowModal(true)
    }

    const handleEdit = async (id) => {
        try {
            const product = await ProductsAPI.getById(id)
            setEditingProduct(product)
            setFormData({
                code: product.code,
                name: product.name,
                category_id: product.category_id || '',
                supplier_id: product.supplier_id || '',
                purchase_price: product.purchase_price,
                sale_price: product.sale_price,
                quantity: product.quantity,
                min_quantity: product.min_quantity,
                description: product.description || ''
            })
            setShowModal(true)
        } catch (error) {
            console.error('Error loading product:', error)
            alert('خطأ في تحميل بيانات المنتج')
        }
    }

    const handleDelete = async (id) => {
        if (window.confirm('هل أنت متأكد من حذف هذا المنتج؟')) {
            try {
                await ProductsAPI.delete(id)
                loadData()
            } catch (error) {
                console.error('Error deleting product:', error)
                alert('خطأ في حذف المنتج')
            }
        }
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
            const data = {
                ...formData,
                category_id: formData.category_id ? parseInt(formData.category_id) : null,
                supplier_id: formData.supplier_id ? parseInt(formData.supplier_id) : null,
                purchase_price: parseFloat(formData.purchase_price),
                sale_price: parseFloat(formData.sale_price),
                quantity: parseInt(formData.quantity),
                min_quantity: parseInt(formData.min_quantity)
            }

            if (editingProduct) {
                await ProductsAPI.update(editingProduct.id, data)
            } else {
                await ProductsAPI.create(data)
            }

            setShowModal(false)
            loadData()
        } catch (error) {
            console.error('Error saving product:', error)
            alert(error.response?.data?.detail || 'خطأ في حفظ المنتج')
        }
    }

    const filteredProducts = products.filter(p =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.code.toLowerCase().includes(searchTerm.toLowerCase())
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
                <h1>كارتة الأصناف</h1>
                <button className="btn btn-primary" onClick={handleAdd}>
                    <i className="fas fa-plus"></i> إضافة صنف جديد
                </button>
            </div>

            <div className="card">
                <div className="search-box">
                    <input
                        type="text"
                        placeholder="بحث عن صنف..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                    <i className="fas fa-search"></i>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>كود الصنف</th>
                            <th>اسم الصنف</th>
                            <th>الفئة</th>
                            <th>سعر الشراء</th>
                            <th>سعر البيع</th>
                            <th>الكمية</th>
                            <th>المورد</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredProducts.map(product => (
                            <tr key={product.id}>
                                <td>{product.code}</td>
                                <td>{product.name}</td>
                                <td>{product.category || '-'}</td>
                                <td>{formatCurrency(product.purchase_price)}</td>
                                <td>{formatCurrency(product.sale_price)}</td>
                                <td>
                                    <span className={`status-badge ${product.quantity <= product.min_quantity ? (product.quantity === 0 ? 'danger' : 'warning') : 'success'}`}>
                                        {product.quantity}
                                    </span>
                                </td>
                                <td>{product.supplier || '-'}</td>
                                <td>
                                    <div className="actions">
                                        <button className="action-btn edit" onClick={() => handleEdit(product.id)}>
                                            <i className="fas fa-edit"></i>
                                        </button>
                                        <button className="action-btn delete" onClick={() => handleDelete(product.id)}>
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
                            <h3>{editingProduct ? 'تعديل الصنف' : 'إضافة صنف جديد'}</h3>
                            <button className="modal-close" onClick={() => setShowModal(false)}>&times;</button>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div className="modal-body">
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>كود الصنف</label>
                                        <input
                                            type="text"
                                            className="form-control"
                                            value={formData.code}
                                            onChange={e => setFormData({ ...formData, code: e.target.value })}
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>اسم الصنف</label>
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
                                        <label>الفئة</label>
                                        <select
                                            className="form-control"
                                            value={formData.category_id}
                                            onChange={e => setFormData({ ...formData, category_id: e.target.value })}
                                        >
                                            <option value="">اختر الفئة</option>
                                            {categories.map(cat => (
                                                <option key={cat.id} value={cat.id}>{cat.name_ar || cat.name}</option>
                                            ))}
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label>المورد</label>
                                        <select
                                            className="form-control"
                                            value={formData.supplier_id}
                                            onChange={e => setFormData({ ...formData, supplier_id: e.target.value })}
                                        >
                                            <option value="">اختر المورد</option>
                                            {suppliers.map(sup => (
                                                <option key={sup.id} value={sup.id}>{sup.name}</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>سعر الشراء</label>
                                        <input
                                            type="number"
                                            step="0.01"
                                            className="form-control"
                                            value={formData.purchase_price}
                                            onChange={e => setFormData({ ...formData, purchase_price: e.target.value })}
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>سعر البيع</label>
                                        <input
                                            type="number"
                                            step="0.01"
                                            className="form-control"
                                            value={formData.sale_price}
                                            onChange={e => setFormData({ ...formData, sale_price: e.target.value })}
                                            required
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>الكمية</label>
                                        <input
                                            type="number"
                                            className="form-control"
                                            value={formData.quantity}
                                            onChange={e => setFormData({ ...formData, quantity: e.target.value })}
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>الحد الأدنى</label>
                                        <input
                                            type="number"
                                            className="form-control"
                                            value={formData.min_quantity}
                                            onChange={e => setFormData({ ...formData, min_quantity: e.target.value })}
                                        />
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label>الوصف</label>
                                    <textarea
                                        className="form-control"
                                        rows="3"
                                        value={formData.description}
                                        onChange={e => setFormData({ ...formData, description: e.target.value })}
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

export default Products
