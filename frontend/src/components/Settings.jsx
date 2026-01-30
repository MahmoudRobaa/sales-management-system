import { useState, useEffect } from 'react'
import { SettingsAPI, CashAPI } from '../services/api'

function Settings() {
    const [settings, setSettings] = useState({
        store_name: '',
        store_address: '',
        store_phone: '',
        min_stock_alert: '5',
        vat_rate: '15'
    })
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    // Cash management state
    const [cashBalance, setCashBalance] = useState(0)
    const [cashTransactions, setCashTransactions] = useState([])
    const [showCashModal, setShowCashModal] = useState(null) // 'deposit' or 'withdraw'
    const [cashAmount, setCashAmount] = useState('')
    const [cashDescription, setCashDescription] = useState('')
    const [cashLoading, setCashLoading] = useState(false)

    useEffect(() => {
        loadData()
    }, [])

    const loadData = async () => {
        try {
            setLoading(true)
            const [settingsData, cashData, transactionsData] = await Promise.all([
                SettingsAPI.getAll(),
                CashAPI.getBalance().catch(() => ({ balance: 0 })),
                CashAPI.getTransactions(20).catch(() => [])
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

            setCashBalance(cashData?.balance || 0)
            setCashTransactions(transactionsData || [])
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

    // Cash deposit/withdraw handler
    const handleCashSubmit = async (e) => {
        e.preventDefault()
        if (!cashAmount || parseFloat(cashAmount) <= 0) {
            alert('يرجى إدخال مبلغ صحيح')
            return
        }

        setCashLoading(true)
        try {
            if (showCashModal === 'deposit') {
                await CashAPI.deposit(parseFloat(cashAmount), cashDescription)
                alert('تم إضافة رأس المال بنجاح')
            } else {
                await CashAPI.withdraw(parseFloat(cashAmount), cashDescription)
                alert('تم سحب المبلغ بنجاح')
            }
            setShowCashModal(null)
            loadData() // Refresh data
        } catch (error) {
            console.error('Cash operation error:', error)
            alert(error.response?.data?.detail || 'حدث خطأ في العملية')
        } finally {
            setCashLoading(false)
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

            {/* Capital Management Section */}
            <div className="card" style={{ marginBottom: '25px', background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)' }}>
                <div className="card-header" style={{ borderBottom: '1px solid #86efac' }}>
                    <h2><i className="fas fa-cash-register"></i> إدارة رأس المال</h2>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
                    <div>
                        <div style={{ fontSize: '0.9rem', color: '#64748b', marginBottom: '4px' }}>رصيد الصندوق الحالي</div>
                        <div style={{ fontSize: '2rem', fontWeight: '700', color: '#059669' }}>
                            {Number(cashBalance).toLocaleString()} EGP
                        </div>
                    </div>
                    <div style={{ display: 'flex', gap: '10px' }}>
                        <button
                            className="btn btn-success"
                            onClick={() => { setShowCashModal('deposit'); setCashAmount(''); setCashDescription('إضافة رأس مال'); }}
                        >
                            <i className="fas fa-plus"></i> إضافة رأس مال
                        </button>
                        <button
                            className="btn btn-danger"
                            onClick={() => { setShowCashModal('withdraw'); setCashAmount(''); setCashDescription('سحب رأس مال'); }}
                            disabled={cashBalance <= 0}
                        >
                            <i className="fas fa-minus"></i> سحب
                        </button>
                    </div>
                </div>

                {/* Recent Transactions */}
                {cashTransactions.length > 0 && (
                    <div>
                        <h4 style={{ marginBottom: '12px', color: '#374151' }}>آخر الحركات</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>النوع</th>
                                    <th>المبلغ</th>
                                    <th>الرصيد بعد</th>
                                    <th>الوصف</th>
                                    <th>التاريخ</th>
                                </tr>
                            </thead>
                            <tbody>
                                {cashTransactions.slice(0, 10).map(t => (
                                    <tr key={t.id}>
                                        <td>
                                            <span style={{
                                                padding: '4px 10px',
                                                borderRadius: '12px',
                                                fontSize: '0.8rem',
                                                fontWeight: '500',
                                                background: t.transaction_type.includes('income') || t.transaction_type === 'deposit'
                                                    ? '#dcfce7' : '#fee2e2',
                                                color: t.transaction_type.includes('income') || t.transaction_type === 'deposit'
                                                    ? '#166534' : '#991b1b'
                                            }}>
                                                {t.transaction_type === 'deposit' ? 'إيداع' :
                                                    t.transaction_type === 'withdrawal' ? 'سحب' :
                                                        t.transaction_type === 'sale_income' ? 'بيع' :
                                                            t.transaction_type === 'purchase_expense' ? 'شراء' : t.transaction_type}
                                            </span>
                                        </td>
                                        <td style={{
                                            fontWeight: '600',
                                            color: t.transaction_type.includes('income') || t.transaction_type === 'deposit'
                                                ? '#059669' : '#dc2626'
                                        }}>
                                            {t.transaction_type.includes('income') || t.transaction_type === 'deposit' ? '+' : '-'}
                                            {Number(t.amount).toLocaleString()}
                                        </td>
                                        <td>{Number(t.balance_after).toLocaleString()}</td>
                                        <td>{t.description || '-'}</td>
                                        <td style={{ fontSize: '0.85rem', color: '#64748b' }}>
                                            {t.created_at ? new Date(t.created_at).toLocaleDateString('ar-EG') : '-'}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
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

            {/* Cash Deposit/Withdraw Modal */}
            {showCashModal && (
                <div className="modal-overlay" onClick={() => setShowCashModal(null)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '400px' }}>
                        <div className="modal-header" style={{
                            background: showCashModal === 'deposit'
                                ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                                : 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
                        }}>
                            <h3>
                                <i className={`fas fa-${showCashModal === 'deposit' ? 'plus' : 'minus'}`}></i>
                                {showCashModal === 'deposit' ? ' إضافة رأس مال' : ' سحب رأس مال'}
                            </h3>
                            <button className="modal-close" onClick={() => setShowCashModal(null)}>&times;</button>
                        </div>
                        <form onSubmit={handleCashSubmit}>
                            <div className="modal-body">
                                <div className="form-group">
                                    <label>المبلغ (EGP)</label>
                                    <input
                                        type="number"
                                        className="form-control"
                                        value={cashAmount}
                                        onChange={e => setCashAmount(e.target.value)}
                                        placeholder="0.00"
                                        min="0.01"
                                        step="0.01"
                                        required
                                        autoFocus
                                        style={{ fontSize: '1.5rem', textAlign: 'center' }}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>الوصف</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        value={cashDescription}
                                        onChange={e => setCashDescription(e.target.value)}
                                        placeholder={showCashModal === 'deposit' ? 'إضافة رأس مال' : 'سحب رأس مال'}
                                    />
                                </div>
                                {showCashModal === 'withdraw' && (
                                    <div style={{
                                        background: '#fef2f2',
                                        padding: '12px',
                                        borderRadius: '8px',
                                        color: '#991b1b',
                                        fontSize: '0.9rem'
                                    }}>
                                        <i className="fas fa-info-circle"></i> الرصيد المتاح: {Number(cashBalance).toLocaleString()} EGP
                                    </div>
                                )}
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn" onClick={() => setShowCashModal(null)}>إلغاء</button>
                                <button
                                    type="submit"
                                    className={`btn ${showCashModal === 'deposit' ? 'btn-success' : 'btn-danger'}`}
                                    disabled={cashLoading}
                                >
                                    {cashLoading ? 'جاري...' : (showCashModal === 'deposit' ? 'إضافة' : 'سحب')}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </>
    )
}

export default Settings
