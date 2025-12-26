import { useState, useEffect } from 'react'
import { PurchasesAPI } from '../services/api'

function Purchases() {
    const [purchases, setPurchases] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadPurchases()
    }, [])

    const loadPurchases = async () => {
        try {
            setLoading(true)
            const data = await PurchasesAPI.getAll()
            setPurchases(data)
        } catch (error) {
            console.error('Error loading purchases:', error)
        } finally {
            setLoading(false)
        }
    }

    const formatCurrency = (amount) => parseFloat(amount || 0).toFixed(2) + ' ج.م'

    const handleDelete = async (id) => {
        if (window.confirm('هل أنت متأكد من حذف هذه العملية؟')) {
            try {
                await PurchasesAPI.delete(id)
                loadPurchases()
            } catch (error) {
                console.error('Error deleting purchase:', error)
            }
        }
    }

    if (loading) {
        return <div className="loading"><div className="loading-spinner"></div><span>جاري التحميل...</span></div>
    }

    return (
        <>
            <div className="page-header">
                <h1>المشتريات</h1>
            </div>

            <div className="card">
                <table>
                    <thead>
                        <tr>
                            <th>رقم الفاتورة</th>
                            <th>التاريخ</th>
                            <th>المورد</th>
                            <th>الإجمالي</th>
                            <th>المدفوع</th>
                            <th>المتبقي</th>
                            <th>الحالة</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {purchases.length === 0 ? (
                            <tr><td colSpan="8" style={{ textAlign: 'center', padding: '30px' }}>لا توجد مشتريات</td></tr>
                        ) : purchases.map(purchase => (
                            <tr key={purchase.id}>
                                <td>{purchase.invoice_no}</td>
                                <td>{purchase.purchase_date}</td>
                                <td>{purchase.supplier_name || '-'}</td>
                                <td>{formatCurrency(purchase.total)}</td>
                                <td>{formatCurrency(purchase.paid)}</td>
                                <td>{formatCurrency(purchase.remaining)}</td>
                                <td><span className={`status-badge ${purchase.status === 'مدفوعة' ? 'success' : purchase.status === 'جزئي' ? 'info' : 'danger'}`}>{purchase.status}</span></td>
                                <td>
                                    <div className="actions">
                                        <button className="action-btn delete" onClick={() => handleDelete(purchase.id)}>
                                            <i className="fas fa-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </>
    )
}

export default Purchases
