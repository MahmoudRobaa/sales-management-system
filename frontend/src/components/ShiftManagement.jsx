import { useState, useEffect } from 'react'
import { ShiftsAPI } from '../services/api'

const getErrorMessage = (error, fallback = 'حدث خطأ') => {
    const detail = error?.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) return detail.map(d => d.msg || d.message || JSON.stringify(d)).join(', ')
    return error?.message || fallback
}

function ShiftManagement() {
    const [shifts, setShifts] = useState([])
    const [currentShift, setCurrentShift] = useState(null)
    const [loading, setLoading] = useState(true)
    const [showOpenModal, setShowOpenModal] = useState(false)
    const [showCloseModal, setShowCloseModal] = useState(false)
    const [showDrawerModal, setShowDrawerModal] = useState(false)
    const [showReconciliation, setShowReconciliation] = useState(null)
    const [reconciliationData, setReconciliationData] = useState(null)
    const [reconciliationLoading, setReconciliationLoading] = useState(false)
    const [openingBalance, setOpeningBalance] = useState('')
    const [closingBalance, setClosingBalance] = useState('')
    const [closeNotes, setCloseNotes] = useState('')
    const [drawerForm, setDrawerForm] = useState({ action: 'cash_in', amount: '', reason: '' })
    const [drawerLogs, setDrawerLogs] = useState([])

    useEffect(() => { loadData() }, [])

    const loadData = async () => {
        try {
            setLoading(true)
            const [allShifts, current] = await Promise.all([
                ShiftsAPI.getAll(),
                ShiftsAPI.getCurrent().catch(() => null)
            ])
            setShifts(allShifts)
            setCurrentShift(current)
            if (current) {
                try {
                    const logs = await ShiftsAPI.getDrawerLogs(current.id)
                    setDrawerLogs(logs)
                } catch { setDrawerLogs([]) }
            }
        } catch (error) {
            console.error('Error loading shifts:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleOpenShift = async () => {
        try {
            await ShiftsAPI.open({ opening_balance: parseFloat(openingBalance || 0) })
            setShowOpenModal(false)
            setOpeningBalance('')
            loadData()
        } catch (error) {
            alert(getErrorMessage(error, 'خطأ في فتح الوردية'))
        }
    }

    const handleCloseShift = async () => {
        try {
            const result = await ShiftsAPI.close({
                closing_balance: parseFloat(closingBalance || 0),
                notes: closeNotes
            })
            alert(`تم إغلاق الوردية بنجاح.\nالرصيد المتوقع: ${formatCurrency(result.expected_balance)}\nالرصيد الفعلي: ${formatCurrency(result.closing_balance)}\nالفرق: ${formatCurrency(result.variance)}`)
            setShowCloseModal(false)
            setClosingBalance('')
            setCloseNotes('')
            loadData()
        } catch (error) {
            alert(getErrorMessage(error, 'خطأ في إغلاق الوردية'))
        }
    }

    const handleDrawerLog = async () => {
        if (!drawerForm.amount) return
        try {
            await ShiftsAPI.addDrawerLog({
                action: drawerForm.action,
                amount: parseFloat(drawerForm.amount),
                reason: drawerForm.reason
            })
            setShowDrawerModal(false)
            setDrawerForm({ action: 'cash_in', amount: '', reason: '' })
            loadData()
        } catch (error) {
            alert(getErrorMessage(error, 'خطأ في تسجيل حركة الدرج'))
        }
    }

    const loadReconciliation = async (shiftId) => {
        setReconciliationLoading(true)
        try {
            const data = await ShiftsAPI.getReconciliation(shiftId)
            setReconciliationData(data)
            setShowReconciliation(shiftId)
        } catch (error) {
            alert(getErrorMessage(error, 'خطأ في تحميل تقرير التسوية'))
        } finally {
            setReconciliationLoading(false)
        }
    }

    const formatCurrency = (amount) => parseFloat(amount || 0).toFixed(2) + ' ج.م'
    const formatDateTime = (dt) => dt ? new Date(dt).toLocaleString('ar-EG') : '-'
    const formatTime = (dt) => dt ? new Date(dt).toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' }) : '-'

    const getElapsedTime = (startTime) => {
        if (!startTime) return ''
        const diff = Date.now() - new Date(startTime).getTime()
        const hours = Math.floor(diff / 3600000)
        const mins = Math.floor((diff % 3600000) / 60000)
        return `${hours} ساعة ${mins} دقيقة`
    }

    if (loading) return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
            <div style={{ textAlign: 'center' }}>
                <i className="fas fa-spinner fa-spin" style={{ fontSize: '2rem', color: 'var(--color-primary)', marginBottom: '12px' }}></i>
                <p style={{ color: 'var(--color-text-secondary)' }}>جاري تحميل الورديات...</p>
            </div>
        </div>
    )

    return (
        <div>
            {/* Page Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <div>
                    <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 'var(--font-weight-bold)', color: 'var(--color-text-primary)', margin: 0 }}>
                        <i className="fas fa-clock" style={{ marginLeft: '10px', color: 'var(--color-primary)' }}></i>
                        إدارة الورديات
                    </h1>
                    <p style={{ color: 'var(--color-text-secondary)', marginTop: '4px', fontSize: 'var(--font-size-sm)' }}>
                        إدارة ورديات الكاشير ومتابعة حركات درج النقدية
                    </p>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                    {currentShift ? (
                        <>
                            <button className="btn btn-warning" onClick={() => setShowDrawerModal(true)} style={{ borderRadius: 'var(--radius-md)', padding: '10px 20px' }}>
                                <i className="fas fa-cash-register" style={{ marginLeft: '6px' }}></i> حركة درج
                            </button>
                            <button className="btn btn-danger" onClick={() => setShowCloseModal(true)} style={{ borderRadius: 'var(--radius-md)', padding: '10px 20px' }}>
                                <i className="fas fa-lock" style={{ marginLeft: '6px' }}></i> إغلاق الوردية
                            </button>
                        </>
                    ) : (
                        <button className="btn btn-primary" onClick={() => setShowOpenModal(true)} style={{ borderRadius: 'var(--radius-md)', padding: '10px 24px', fontSize: 'var(--font-size-base)' }}>
                            <i className="fas fa-lock-open" style={{ marginLeft: '6px' }}></i> فتح وردية جديدة
                        </button>
                    )}
                </div>
            </div>

            {/* Current Shift Status Card */}
            {currentShift && (
                <div style={{
                    background: 'linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%)',
                    borderRadius: 'var(--radius-lg)',
                    padding: '24px',
                    marginBottom: '24px',
                    color: 'white',
                    boxShadow: 'var(--shadow-lg)'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                                <span style={{ background: 'rgba(255,255,255,0.2)', padding: '4px 12px', borderRadius: 'var(--radius-full)', fontSize: 'var(--font-size-sm)' }}>
                                    <i className="fas fa-circle" style={{ color: '#4ade80', fontSize: '8px', marginLeft: '6px' }}></i>
                                    وردية مفتوحة
                                </span>
                                <span style={{ opacity: 0.8, fontSize: 'var(--font-size-sm)' }}>#{currentShift.id}</span>
                            </div>
                            <h3 style={{ marginBottom: '4px', fontWeight: 'var(--font-weight-semibold)' }}>
                                الكاشير: {currentShift.cashier_name || 'غير محدد'}
                            </h3>
                            <p style={{ opacity: 0.8, fontSize: 'var(--font-size-sm)' }}>
                                بدأت في: {formatDateTime(currentShift.start_time)}
                            </p>
                        </div>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: 'var(--font-size-sm)', opacity: 0.8, marginBottom: '4px' }}>المدة</div>
                            <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 'var(--font-weight-bold)' }}>
                                {getElapsedTime(currentShift.start_time)}
                            </div>
                        </div>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginTop: '20px' }}>
                        <div style={{ background: 'rgba(255,255,255,0.15)', borderRadius: 'var(--radius-md)', padding: '16px', textAlign: 'center' }}>
                            <div style={{ fontSize: 'var(--font-size-sm)', opacity: 0.8, marginBottom: '4px' }}>الرصيد الافتتاحي</div>
                            <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 'var(--font-weight-bold)' }}>{formatCurrency(currentShift.opening_balance)}</div>
                        </div>
                        <div style={{ background: 'rgba(255,255,255,0.15)', borderRadius: 'var(--radius-md)', padding: '16px', textAlign: 'center' }}>
                            <div style={{ fontSize: 'var(--font-size-sm)', opacity: 0.8, marginBottom: '4px' }}>المبيعات</div>
                            <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 'var(--font-weight-bold)' }}>{currentShift.total_sales || 0}</div>
                        </div>
                        <div style={{ background: 'rgba(255,255,255,0.15)', borderRadius: 'var(--radius-md)', padding: '16px', textAlign: 'center' }}>
                            <div style={{ fontSize: 'var(--font-size-sm)', opacity: 0.8, marginBottom: '4px' }}>حركات الدرج</div>
                            <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 'var(--font-weight-bold)' }}>{drawerLogs.length}</div>
                        </div>
                    </div>

                    {/* Drawer Logs Quick View */}
                    {drawerLogs.length > 0 && (
                        <div style={{ marginTop: '16px', background: 'rgba(255,255,255,0.1)', borderRadius: 'var(--radius-md)', padding: '12px' }}>
                            <div style={{ fontSize: 'var(--font-size-sm)', fontWeight: 'var(--font-weight-semibold)', marginBottom: '8px' }}>
                                <i className="fas fa-exchange-alt" style={{ marginLeft: '6px' }}></i> آخر حركات الدرج
                            </div>
                            {drawerLogs.slice(0, 3).map((log, i) => (
                                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: i < 2 ? '1px solid rgba(255,255,255,0.1)' : 'none', fontSize: 'var(--font-size-sm)' }}>
                                    <span>
                                        <i className={`fas fa-arrow-${log.action === 'cash_in' ? 'down' : 'up'}`} style={{ marginLeft: '6px', color: log.action === 'cash_in' ? '#4ade80' : '#fb923c' }}></i>
                                        {log.action === 'cash_in' ? 'إيداع' : 'سحب'} — {log.reason || ''}
                                    </span>
                                    <span style={{ fontWeight: 'var(--font-weight-semibold)' }}>{formatCurrency(log.amount)}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* No Active Shift Notice */}
            {!currentShift && (
                <div style={{
                    background: 'var(--color-warning-light)',
                    border: '1px solid var(--color-warning)',
                    borderRadius: 'var(--radius-lg)',
                    padding: '24px',
                    marginBottom: '24px',
                    textAlign: 'center'
                }}>
                    <i className="fas fa-exclamation-triangle" style={{ fontSize: '2rem', color: 'var(--color-warning-dark)', marginBottom: '12px' }}></i>
                    <h3 style={{ color: 'var(--color-warning-dark)', marginBottom: '8px' }}>لا توجد وردية مفتوحة</h3>
                    <p style={{ color: 'var(--color-text-secondary)', marginBottom: '16px' }}>يجب فتح وردية لبدء عمليات البيع وتسجيل حركات الدرج</p>
                    <button className="btn btn-primary" onClick={() => setShowOpenModal(true)} style={{ borderRadius: 'var(--radius-md)', padding: '10px 24px' }}>
                        <i className="fas fa-lock-open" style={{ marginLeft: '6px' }}></i> فتح وردية جديدة
                    </button>
                </div>
            )}

            {/* Shifts History Table */}
            <div style={{ background: 'var(--color-surface)', borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-sm)', overflow: 'hidden' }}>
                <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--color-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h3 style={{ margin: 0, fontSize: 'var(--font-size-lg)', fontWeight: 'var(--font-weight-semibold)' }}>
                        <i className="fas fa-history" style={{ marginLeft: '8px', color: 'var(--color-text-secondary)' }}></i>
                        سجل الورديات
                    </h3>
                    <span style={{ background: 'var(--color-primary-light)', color: 'var(--color-primary)', padding: '4px 12px', borderRadius: 'var(--radius-full)', fontSize: 'var(--font-size-sm)', fontWeight: 'var(--font-weight-semibold)' }}>
                        {shifts.length} وردية
                    </span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th style={{ padding: '12px 16px' }}>#</th>
                            <th style={{ padding: '12px 16px' }}>البداية</th>
                            <th style={{ padding: '12px 16px' }}>النهاية</th>
                            <th style={{ padding: '12px 16px' }}>الرصيد الافتتاحي</th>
                            <th style={{ padding: '12px 16px' }}>الرصيد الختامي</th>
                            <th style={{ padding: '12px 16px' }}>الفرق</th>
                            <th style={{ padding: '12px 16px' }}>الحالة</th>
                            <th style={{ padding: '12px 16px' }}>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {shifts.map(s => (
                            <tr key={s.id} style={{ borderBottom: '1px solid var(--color-border-light)' }}>
                                <td style={{ padding: '12px 16px', fontWeight: 'var(--font-weight-semibold)' }}>{s.id}</td>
                                <td style={{ padding: '12px 16px', fontSize: 'var(--font-size-sm)' }}>{formatDateTime(s.start_time)}</td>
                                <td style={{ padding: '12px 16px', fontSize: 'var(--font-size-sm)' }}>{formatDateTime(s.end_time)}</td>
                                <td style={{ padding: '12px 16px' }}>{formatCurrency(s.opening_balance)}</td>
                                <td style={{ padding: '12px 16px' }}>{s.closing_balance != null ? formatCurrency(s.closing_balance) : '-'}</td>
                                <td style={{
                                    padding: '12px 16px',
                                    fontWeight: 'var(--font-weight-semibold)',
                                    color: s.variance && s.variance !== 0 ? (s.variance > 0 ? 'var(--color-success)' : 'var(--color-danger)') : 'var(--color-text-secondary)'
                                }}>
                                    {s.variance != null ? formatCurrency(s.variance) : '-'}
                                </td>
                                <td style={{ padding: '12px 16px' }}>
                                    <span style={{
                                        padding: '4px 12px',
                                        borderRadius: 'var(--radius-full)',
                                        fontSize: 'var(--font-size-xs)',
                                        fontWeight: 'var(--font-weight-semibold)',
                                        background: s.status === 'open' ? 'var(--color-success-light)' : '#f1f5f9',
                                        color: s.status === 'open' ? 'var(--color-success-dark)' : 'var(--color-text-secondary)'
                                    }}>
                                        <i className={`fas fa-${s.status === 'open' ? 'circle' : 'check-circle'}`} style={{ marginLeft: '4px', fontSize: '8px' }}></i>
                                        {s.status === 'open' ? 'مفتوحة' : 'مغلقة'}
                                    </span>
                                </td>
                                <td style={{ padding: '12px 16px' }}>
                                    <button
                                        className="btn btn-sm"
                                        onClick={() => loadReconciliation(s.id)}
                                        title="تقرير التسوية"
                                        disabled={reconciliationLoading}
                                        style={{
                                            background: 'var(--color-info-light)',
                                            color: 'var(--color-info-dark)',
                                            border: 'none',
                                            borderRadius: 'var(--radius-sm)',
                                            padding: '6px 14px',
                                            cursor: 'pointer',
                                            fontSize: 'var(--font-size-sm)'
                                        }}
                                    >
                                        <i className="fas fa-file-alt" style={{ marginLeft: '4px' }}></i> تسوية
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {shifts.length === 0 && (
                            <tr>
                                <td colSpan="8" style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-muted)' }}>
                                    <i className="fas fa-inbox" style={{ fontSize: '2rem', marginBottom: '12px', display: 'block' }}></i>
                                    لا توجد ورديات مسجلة بعد
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Open Shift Modal */}
            {showOpenModal && (
                <div className="modal-overlay" onClick={() => setShowOpenModal(false)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '440px' }}>
                        <div className="modal-header" style={{ background: 'linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%)', color: 'white' }}>
                            <h3><i className="fas fa-lock-open" style={{ marginLeft: '8px' }}></i> فتح وردية جديدة</h3>
                            <button className="modal-close" onClick={() => setShowOpenModal(false)} style={{ color: 'white' }}>&times;</button>
                        </div>
                        <div className="modal-body" style={{ padding: '24px' }}>
                            <div style={{ background: 'var(--color-info-light)', padding: '12px 16px', borderRadius: 'var(--radius-md)', marginBottom: '20px', fontSize: 'var(--font-size-sm)', color: 'var(--color-info-dark)' }}>
                                <i className="fas fa-info-circle" style={{ marginLeft: '6px' }}></i>
                                أدخل المبلغ المتاح في الدرج عند بدء الوردية
                            </div>
                            <div className="form-group">
                                <label style={{ fontWeight: 'var(--font-weight-semibold)' }}>الرصيد الافتتاحي (ج.م)</label>
                                <input type="number" step="0.01" className="form-control" value={openingBalance} onChange={e => setOpeningBalance(e.target.value)} placeholder="0.00" style={{ fontSize: 'var(--font-size-lg)', padding: '12px', textAlign: 'center' }} />
                            </div>
                        </div>
                        <div className="modal-footer">
                            <button className="btn" onClick={() => setShowOpenModal(false)}>إلغاء</button>
                            <button className="btn btn-primary" onClick={handleOpenShift} style={{ borderRadius: 'var(--radius-md)' }}>
                                <i className="fas fa-play" style={{ marginLeft: '6px' }}></i> فتح الوردية
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Close Shift Modal */}
            {showCloseModal && (
                <div className="modal-overlay" onClick={() => setShowCloseModal(false)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '480px' }}>
                        <div className="modal-header" style={{ background: 'linear-gradient(135deg, var(--color-danger) 0%, var(--color-danger-dark) 100%)', color: 'white' }}>
                            <h3><i className="fas fa-lock" style={{ marginLeft: '8px' }}></i> إغلاق الوردية</h3>
                            <button className="modal-close" onClick={() => setShowCloseModal(false)} style={{ color: 'white' }}>&times;</button>
                        </div>
                        <div className="modal-body" style={{ padding: '24px' }}>
                            {currentShift && (
                                <div style={{ background: '#f8fafc', padding: '16px', borderRadius: 'var(--radius-md)', marginBottom: '20px' }}>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: 'var(--font-size-sm)' }}>
                                        <div><span style={{ color: 'var(--color-text-secondary)' }}>الرصيد الافتتاحي:</span> <strong>{formatCurrency(currentShift.opening_balance)}</strong></div>
                                        <div><span style={{ color: 'var(--color-text-secondary)' }}>وقت البدء:</span> <strong>{formatTime(currentShift.start_time)}</strong></div>
                                        <div><span style={{ color: 'var(--color-text-secondary)' }}>المدة:</span> <strong>{getElapsedTime(currentShift.start_time)}</strong></div>
                                        <div><span style={{ color: 'var(--color-text-secondary)' }}>حركات الدرج:</span> <strong>{drawerLogs.length}</strong></div>
                                    </div>
                                </div>
                            )}
                            <div className="form-group">
                                <label style={{ fontWeight: 'var(--font-weight-semibold)' }}>الرصيد الختامي الفعلي (ج.م)</label>
                                <input type="number" step="0.01" className="form-control" value={closingBalance} onChange={e => setClosingBalance(e.target.value)} placeholder="عد النقدية في الدرج" style={{ fontSize: 'var(--font-size-lg)', padding: '12px', textAlign: 'center' }} />
                            </div>
                            <div className="form-group">
                                <label style={{ fontWeight: 'var(--font-weight-semibold)' }}>ملاحظات</label>
                                <textarea className="form-control" value={closeNotes} onChange={e => setCloseNotes(e.target.value)} placeholder="ملاحظات اختيارية عن الوردية" rows="2" />
                            </div>
                        </div>
                        <div className="modal-footer">
                            <button className="btn" onClick={() => setShowCloseModal(false)}>إلغاء</button>
                            <button className="btn btn-danger" onClick={handleCloseShift} style={{ borderRadius: 'var(--radius-md)' }}>
                                <i className="fas fa-lock" style={{ marginLeft: '6px' }}></i> إغلاق الوردية
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Drawer Log Modal */}
            {showDrawerModal && (
                <div className="modal-overlay" onClick={() => setShowDrawerModal(false)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '440px' }}>
                        <div className="modal-header" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', color: 'white' }}>
                            <h3><i className="fas fa-cash-register" style={{ marginLeft: '8px' }}></i> حركة درج النقدية</h3>
                            <button className="modal-close" onClick={() => setShowDrawerModal(false)} style={{ color: 'white' }}>&times;</button>
                        </div>
                        <div className="modal-body" style={{ padding: '24px' }}>
                            <div className="form-group">
                                <label style={{ fontWeight: 'var(--font-weight-semibold)' }}>نوع الحركة</label>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                                    <button
                                        type="button"
                                        onClick={() => setDrawerForm(prev => ({ ...prev, action: 'cash_in' }))}
                                        style={{
                                            padding: '12px',
                                            border: `2px solid ${drawerForm.action === 'cash_in' ? 'var(--color-success)' : 'var(--color-border)'}`,
                                            borderRadius: 'var(--radius-md)',
                                            background: drawerForm.action === 'cash_in' ? 'var(--color-success-light)' : 'white',
                                            cursor: 'pointer',
                                            fontWeight: 'var(--font-weight-semibold)',
                                            color: drawerForm.action === 'cash_in' ? 'var(--color-success-dark)' : 'var(--color-text-secondary)'
                                        }}
                                    >
                                        <i className="fas fa-arrow-down" style={{ marginLeft: '6px' }}></i> إيداع
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => setDrawerForm(prev => ({ ...prev, action: 'cash_out' }))}
                                        style={{
                                            padding: '12px',
                                            border: `2px solid ${drawerForm.action === 'cash_out' ? 'var(--color-danger)' : 'var(--color-border)'}`,
                                            borderRadius: 'var(--radius-md)',
                                            background: drawerForm.action === 'cash_out' ? 'var(--color-danger-light)' : 'white',
                                            cursor: 'pointer',
                                            fontWeight: 'var(--font-weight-semibold)',
                                            color: drawerForm.action === 'cash_out' ? 'var(--color-danger-dark)' : 'var(--color-text-secondary)'
                                        }}
                                    >
                                        <i className="fas fa-arrow-up" style={{ marginLeft: '6px' }}></i> سحب
                                    </button>
                                </div>
                            </div>
                            <div className="form-group">
                                <label style={{ fontWeight: 'var(--font-weight-semibold)' }}>المبلغ (ج.م)</label>
                                <input type="number" step="0.01" className="form-control" value={drawerForm.amount} onChange={e => setDrawerForm(prev => ({ ...prev, amount: e.target.value }))} placeholder="0.00" style={{ fontSize: 'var(--font-size-lg)', padding: '12px', textAlign: 'center' }} />
                            </div>
                            <div className="form-group">
                                <label style={{ fontWeight: 'var(--font-weight-semibold)' }}>السبب</label>
                                <input type="text" className="form-control" value={drawerForm.reason} onChange={e => setDrawerForm(prev => ({ ...prev, reason: e.target.value }))} placeholder="مثال: فكة - مصروفات - سلفة" />
                            </div>
                        </div>
                        <div className="modal-footer">
                            <button className="btn" onClick={() => setShowDrawerModal(false)}>إلغاء</button>
                            <button className="btn btn-primary" onClick={handleDrawerLog} disabled={!drawerForm.amount} style={{ borderRadius: 'var(--radius-md)' }}>
                                <i className="fas fa-check" style={{ marginLeft: '6px' }}></i> تسجيل الحركة
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Reconciliation Modal */}
            {showReconciliation && reconciliationData && (
                <div className="modal-overlay" onClick={() => setShowReconciliation(null)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '560px' }}>
                        <div className="modal-header" style={{ background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)', color: 'white' }}>
                            <h3><i className="fas fa-file-alt" style={{ marginLeft: '8px' }}></i> تقرير تسوية الوردية #{showReconciliation}</h3>
                            <button className="modal-close" onClick={() => setShowReconciliation(null)} style={{ color: 'white' }}>&times;</button>
                        </div>
                        <div className="modal-body" style={{ padding: '24px' }}>
                            {/* Summary Cards */}
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px' }}>
                                <div style={{ background: '#f0fdf4', borderRadius: 'var(--radius-md)', padding: '16px', borderRight: '4px solid var(--color-success)' }}>
                                    <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>الرصيد الافتتاحي</div>
                                    <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 'var(--font-weight-bold)', color: 'var(--color-success-dark)' }}>{formatCurrency(reconciliationData.opening_balance)}</div>
                                </div>
                                <div style={{ background: '#eff6ff', borderRadius: 'var(--radius-md)', padding: '16px', borderRight: '4px solid var(--color-info)' }}>
                                    <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>الرصيد المتوقع</div>
                                    <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 'var(--font-weight-bold)', color: 'var(--color-info-dark)' }}>{formatCurrency(reconciliationData.expected_balance)}</div>
                                </div>
                                <div style={{ background: '#fefce8', borderRadius: 'var(--radius-md)', padding: '16px', borderRight: '4px solid var(--color-warning)' }}>
                                    <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>الرصيد الفعلي</div>
                                    <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 'var(--font-weight-bold)', color: 'var(--color-warning-dark)' }}>{formatCurrency(reconciliationData.closing_balance)}</div>
                                </div>
                                <div style={{
                                    background: reconciliationData.variance == 0 ? '#f0fdf4' : '#fef2f2',
                                    borderRadius: 'var(--radius-md)',
                                    padding: '16px',
                                    borderRight: `4px solid ${reconciliationData.variance == 0 ? 'var(--color-success)' : 'var(--color-danger)'}`
                                }}>
                                    <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>الفرق</div>
                                    <div style={{
                                        fontSize: 'var(--font-size-xl)',
                                        fontWeight: 'var(--font-weight-bold)',
                                        color: reconciliationData.variance == 0 ? 'var(--color-success-dark)' : 'var(--color-danger-dark)'
                                    }}>
                                        {formatCurrency(reconciliationData.variance)}
                                        {reconciliationData.variance == 0 && <i className="fas fa-check-circle" style={{ marginRight: '8px', fontSize: 'var(--font-size-base)' }}></i>}
                                    </div>
                                </div>
                            </div>

                            {/* Sales Summary */}
                            <div style={{ background: '#f8fafc', borderRadius: 'var(--radius-md)', padding: '16px', marginBottom: '16px' }}>
                                <h4 style={{ marginBottom: '12px', fontSize: 'var(--font-size-sm)', fontWeight: 'var(--font-weight-semibold)' }}>
                                    <i className="fas fa-chart-bar" style={{ marginLeft: '6px', color: 'var(--color-primary)' }}></i> ملخص المبيعات
                                </h4>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: 'var(--font-size-sm)' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <span style={{ color: 'var(--color-text-secondary)' }}>إجمالي المبيعات:</span>
                                        <strong>{formatCurrency(reconciliationData.total_sales)}</strong>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <span style={{ color: 'var(--color-text-secondary)' }}>عدد الفواتير:</span>
                                        <strong>{reconciliationData.sales_count || 0}</strong>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <span style={{ color: 'var(--color-text-secondary)' }}>إجمالي المرتجعات:</span>
                                        <strong>{formatCurrency(reconciliationData.total_returns)}</strong>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <span style={{ color: 'var(--color-text-secondary)' }}>عدد المرتجعات:</span>
                                        <strong>{reconciliationData.returns_count || 0}</strong>
                                    </div>
                                </div>
                            </div>

                            {/* Payment Breakdown */}
                            {reconciliationData.payment_breakdown && Object.keys(reconciliationData.payment_breakdown).length > 0 && (
                                <div style={{ marginBottom: '16px' }}>
                                    <h4 style={{ marginBottom: '12px', fontSize: 'var(--font-size-sm)', fontWeight: 'var(--font-weight-semibold)' }}>
                                        <i className="fas fa-money-bill-wave" style={{ marginLeft: '6px', color: 'var(--color-success)' }}></i> توزيع طرق الدفع
                                    </h4>
                                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                        <thead>
                                            <tr style={{ background: '#f1f5f9' }}>
                                                <th style={{ padding: '10px 12px', textAlign: 'right', fontSize: 'var(--font-size-sm)' }}>الطريقة</th>
                                                <th style={{ padding: '10px 12px', textAlign: 'center', fontSize: 'var(--font-size-sm)' }}>العدد</th>
                                                <th style={{ padding: '10px 12px', textAlign: 'left', fontSize: 'var(--font-size-sm)' }}>الإجمالي</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {Object.entries(reconciliationData.payment_breakdown).map(([method, data]) => (
                                                <tr key={method} style={{ borderBottom: '1px solid var(--color-border-light)' }}>
                                                    <td style={{ padding: '10px 12px', fontWeight: 'var(--font-weight-medium)' }}>{method}</td>
                                                    <td style={{ padding: '10px 12px', textAlign: 'center' }}>{data.count}</td>
                                                    <td style={{ padding: '10px 12px', fontWeight: 'var(--font-weight-semibold)' }}>{formatCurrency(data.total)}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}

                            {/* Drawer Logs */}
                            {reconciliationData.drawer_logs && reconciliationData.drawer_logs.length > 0 && (
                                <div>
                                    <h4 style={{ marginBottom: '12px', fontSize: 'var(--font-size-sm)', fontWeight: 'var(--font-weight-semibold)' }}>
                                        <i className="fas fa-exchange-alt" style={{ marginLeft: '6px', color: 'var(--color-warning)' }}></i> حركات الدرج
                                    </h4>
                                    {reconciliationData.drawer_logs.map((log, i) => (
                                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', borderBottom: '1px solid var(--color-border-light)', fontSize: 'var(--font-size-sm)' }}>
                                            <div>
                                                <span style={{
                                                    padding: '2px 8px',
                                                    borderRadius: 'var(--radius-full)',
                                                    fontSize: 'var(--font-size-xs)',
                                                    background: log.action === 'cash_in' ? 'var(--color-success-light)' : 'var(--color-danger-light)',
                                                    color: log.action === 'cash_in' ? 'var(--color-success-dark)' : 'var(--color-danger-dark)'
                                                }}>
                                                    {log.action === 'cash_in' ? 'إيداع' : 'سحب'}
                                                </span>
                                                <span style={{ marginRight: '8px', color: 'var(--color-text-secondary)' }}>{log.reason || ''}</span>
                                            </div>
                                            <strong style={{ color: log.action === 'cash_in' ? 'var(--color-success)' : 'var(--color-danger)' }}>
                                                {log.action === 'cash_in' ? '+' : '-'}{formatCurrency(log.amount)}
                                            </strong>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                        <div className="modal-footer">
                            <button className="btn" onClick={() => setShowReconciliation(null)} style={{ borderRadius: 'var(--radius-md)' }}>إغلاق</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default ShiftManagement
