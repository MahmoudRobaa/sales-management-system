import { useState, useEffect } from 'react'
import { SettingsAPI, CategoriesAPI } from '../services/api'

function Settings() {
    const [settings, setSettings] = useState({
        store_name: '',
        store_address: '',
        store_phone: '',
        min_stock_alert: '5',
        vat_rate: '15'
    })
    const [categories, setCategories] = useState([])
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [showCategoryModal, setShowCategoryModal] = useState(false)
    const [editingCategory, setEditingCategory] = useState(null)
    const [categoryForm, setCategoryForm] = useState({ code: '', name: '', name_ar: '', description: '' })

    useEffect(() => {
        loadData()
    }, [])

    const loadData = async () => {
        try {
            setLoading(true)
            const [settingsData, categoriesData] = await Promise.all([
                SettingsAPI.getAll(),
                CategoriesAPI.getAll()
            ])

            const settingsObj = {}
            settingsData.forEach(s => {
                settingsObj[s.key] = s.value || ''
            })
            setSettings({
                store_name: settingsObj.store_name || '',
                store_address: settingsObj.store_address || '',
                store_phone: settingsObj.store_phone || '',
                min_stock_alert: settingsObj.min_stock_alert || '5',
                vat_rate: settingsObj.vat_rate || '15'
            })

            setCategories(categoriesData)
        } catch (error) {
            console.error('Error loading settings:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
            setSaving(true)
            await SettingsAPI.update([
                { key: 'store_name', value: settings.store_name },
                { key: 'store_address', value: settings.store_address },
                { key: 'store_phone', value: settings.store_phone },
                { key: 'min_stock_alert', value: settings.min_stock_alert },
                { key: 'vat_rate', value: settings.vat_rate }
            ])
            alert('تم حفظ الإعدادات بنجاح')
        } catch (error) {
            console.error('Error saving settings:', error)
            alert('خطأ في حفظ الإعدادات')
        } finally {
            setSaving(false)
        }
    }

    // Category Management
    const openAddCategory = () => {
        setEditingCategory(null)
        setCategoryForm({
            code: `CAT${String(categories.length + 1).padStart(3, '0')}`,
            name: '',
            name_ar: '',
            description: ''
        })
        setShowCategoryModal(true)
    }

    const openEditCategory = (category) => {
        setEditingCategory(category)
        setCategoryForm({
            code: category.code,
            name: category.name,
            name_ar: category.name_ar || '',
            description: category.description || ''
        })
        setShowCategoryModal(true)
    }

    const handleCategorySubmit = async (e) => {
        e.preventDefault()
        try {
            if (editingCategory) {
                await CategoriesAPI.update(editingCategory.id, categoryForm)
            } else {
                await CategoriesAPI.create(categoryForm)
            }
            setShowCategoryModal(false)
            loadData()
        } catch (error) {
            console.error('Error saving category:', error)
            alert(error.response?.data?.detail || 'خطأ في حفظ الفئة')
        }
    }

    const handleDeleteCategory = async (id) => {
        if (window.confirm('هل أنت متأكد من حذف هذه الفئة؟')) {
            try {
                await CategoriesAPI.delete(id)
                loadData()
            } catch (error) {
                console.error('Error deleting category:', error)
                alert(error.response?.data?.detail || 'خطأ في حذف الفئة - قد تكون مرتبطة بمنتجات')
            }
        }
    }

    if (loading) {
        return <div className="loading"><div className="loading-spinner"></div><span>جاري التحميل...</span></div>
    }

    return (
        <>
            <div className="page-header">
                <h1>الإعدادات</h1>
            </div>

            {/* Store Settings */}
            <div className="card" style={{ marginBottom: '25px' }}>
                <div className="card-header">
                    <h2><i className="fas fa-store"></i> إعدادات المحل</h2>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>اسم المحل</label>
                        <input
                            type="text"
                            className="form-control"
                            value={settings.store_name}
                            onChange={e => setSettings({ ...settings, store_name: e.target.value })}
                            placeholder="مثال: محل الحاسوب والأدوات الكهربائية"
                        />
                    </div>

                    <div className="form-group">
                        <label>عنوان المحل</label>
                        <input
                            type="text"
                            className="form-control"
                            value={settings.store_address}
                            onChange={e => setSettings({ ...settings, store_address: e.target.value })}
                            placeholder="مثال: شارع الرئيسي - المدينة"
                        />
                    </div>

                    <div className="form-group">
                        <label>رقم الهاتف</label>
                        <input
                            type="text"
                            className="form-control"
                            value={settings.store_phone}
                            onChange={e => setSettings({ ...settings, store_phone: e.target.value })}
                            placeholder="مثال: 01000000000"
                        />
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label>حد التنبيه للمخزون المنخفض</label>
                            <input
                                type="number"
                                className="form-control"
                                value={settings.min_stock_alert}
                                onChange={e => setSettings({ ...settings, min_stock_alert: e.target.value })}
                                min="1"
                            />
                        </div>

                        <div className="form-group">
                            <label>نسبة ضريبة القيمة المضافة (%)</label>
                            <input
                                type="number"
                                className="form-control"
                                value={settings.vat_rate}
                                onChange={e => setSettings({ ...settings, vat_rate: e.target.value })}
                                min="0"
                                step="0.1"
                            />
                        </div>
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={saving}>
                        {saving ? 'جاري الحفظ...' : 'حفظ الإعدادات'}
                    </button>
                </form>
            </div>

            {/* Categories Management */}
            <div className="card">
                <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h2><i className="fas fa-tags"></i> إدارة الفئات (أنواع المنتجات)</h2>
                    <button className="btn btn-primary btn-sm" onClick={openAddCategory}>
                        <i className="fas fa-plus"></i> إضافة فئة
                    </button>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>الكود</th>
                            <th>اسم الفئة</th>
                            <th>الوصف</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {categories.length === 0 ? (
                            <tr><td colSpan="5" style={{ textAlign: 'center', padding: '30px' }}>لا توجد فئات</td></tr>
                        ) : categories.map(cat => (
                            <tr key={cat.id}>
                                <td><code>{cat.code}</code></td>
                                <td>{cat.name_ar || cat.name}</td>
                                <td>{cat.description || '-'}</td>
                                <td>
                                    <div className="actions">
                                        <button className="action-btn edit" onClick={() => openEditCategory(cat)} title="تعديل">
                                            <i className="fas fa-edit"></i>
                                        </button>
                                        <button className="action-btn delete" onClick={() => handleDeleteCategory(cat.id)} title="حذف">
                                            <i className="fas fa-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Category Modal */}
            {showCategoryModal && (
                <div className="modal-overlay" onClick={() => setShowCategoryModal(false)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>{editingCategory ? 'تعديل الفئة' : 'إضافة فئة جديدة'}</h3>
                            <button className="modal-close" onClick={() => setShowCategoryModal(false)}>&times;</button>
                        </div>
                        <form onSubmit={handleCategorySubmit}>
                            <div className="modal-body">
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>الكود</label>
                                        <input
                                            type="text"
                                            className="form-control"
                                            value={categoryForm.code}
                                            onChange={e => setCategoryForm({ ...categoryForm, code: e.target.value })}
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>اسم الفئة</label>
                                        <input
                                            type="text"
                                            className="form-control"
                                            value={categoryForm.name}
                                            onChange={e => setCategoryForm({ ...categoryForm, name: e.target.value, name_ar: e.target.value })}
                                            required
                                            placeholder="مثال: إلكترونيات أو Electronics"
                                        />
                                    </div>
                                </div>
                                <div className="form-group">
                                    <label>الوصف</label>
                                    <textarea
                                        className="form-control"
                                        rows="2"
                                        value={categoryForm.description}
                                        onChange={e => setCategoryForm({ ...categoryForm, description: e.target.value })}
                                    ></textarea>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn" onClick={() => setShowCategoryModal(false)}>إلغاء</button>
                                <button type="submit" className="btn btn-primary">حفظ</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </>
    )
}

export default Settings
