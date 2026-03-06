import { useState, useEffect } from 'react'
import { ShiftsAPI } from '../services/api'

function ShiftManagement() {
    const [shifts, setShifts] = useState([])
    const [currentShift, setCurrentShift] = useState(null)
    const [loading, setLoading] = useState(true)
    const [showOpenModal, setShowOpenModal] = useState(false)
    const [showCloseModal, setShowCloseModal] = useState(false)
    const [showDrawerModal, setShowDrawerModal] = useState(false)
    const [showReconciliation, setShowReconciliation] = useState(null)
    const [reconciliationData, setReconciliationData] = useState(null)
    const [openingBalance, setOpeningBalance] = useState('')
    const [closingBalance, setClosingBalance] = useState('')
    const [closeNotes, setCloseNotes] = useState('')
    const [drawerForm, setDrawerForm] = useState({ action: 'cash_in', amount: '', reason: '' })

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
        } catch (error) {
            console.error('Error loading shifts:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleOpenShift = async () => {
        try {
            await ShiftsAPI.open({ opening_balance: parseFloat(openingBalance || 0) })
            alert('تم فتح الوردية بنجاح')
            setShowOpenModal(false)
            setOpeningBalance('')
            loadData()
        } catch (error) {
            alert(error.response?.data?.detail || 'خطأ في فتح الوردية')
        }
    }

    const handleCloseShift = async () => {
        try {
            const result = await ShiftsAPI.close({
                closing_balance: parseFloat(closingBalance || 0),
                notes: closeNotes
            })
            alert(`تم إغلاق الوردية. الفرق: ${result.variance || 0} ج.م`)
            setShowCloseModal(false)
            setClosingBalance('')
            setCloseNotes('')
            loadData()
        } catch (error) {
            alert(error.response?.data?.detail || 'خطأ في إغلاق الوردية')
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
            alert('تم التسجيل')
            setShowDrawerModal(false)
            setDrawerForm({ action: 'cash_in', amount: '', reason: '' })
            loadData()
        } catch (error) {
            alert(error.response?.data?.detail || 'خطأ')
        }
    }

    const loadReconciliation = async (shiftId) => {
        try {
            const data = await ShiftsAPI.getReconciliation(shiftId)
            setReconciliationData(data)
            setShowReconciliation(shiftId)
        } catch (error) {
            alert('خطأ في تحميل تقرير التسوية')
        }
    }

    const formatCurrency = (amount) => parseFloat(amount || 0).toFixed(2) + ' ج.م'
    const formatDateTime = (dt) => dt ? new Date(dt).toLocaleString('ar-EG') : '-'

    if (loading) return <div className="loading"><div className="spinner"></div></div>

    return (
        <div>
            <div className="section-header">
                <h2><i className="fas fa-clock"></i> إدارة الورديات</h2>
                <div style={{ display: 'flex', gap: '8px' }}>
                    {currentShift ? (
                        <>
                            <span className="badge badge-success" style={{ padding: '8px 16px', fontSize: '14px' }}>
                                وردية مفتوحة منذ {formatDateTime(currentShift.start_time)}
                            </span>
                            <button className="btn btn-warning" onClick={() => setShowDrawerModal(true)}>
                                <i className="fas fa-cash-register"></i> حركة درج
                            </button>
                            <button className="btn btn-danger" onClick={() => setShowCloseModal(true)}>
                                <i className="fas fa-lock"></i> إغلاق الوردية
                            </button>
                        </>
                    ) : (
                        <button className="btn btn-primary" onClick={() => setShowOpenModal(true)}>
                            <i className="fas fa-lock-open"></i> فتح وردية جديدة
                        </button>
                    )}
                </div>
            </div>

            <div className="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>البداية</th>
                            <th>النهاية</th>
                            <th>الرصيد الافتتاحي</th>
                            <th>الرصيد الختامي</th>
                            <th>الفرق</th>
                            <th>الحالة</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {shifts.map(s => (
                            <tr key={s.id}>
                                <td>{s.id}</td>
                                <td>{formatDateTime(s.start_time)}</td>
                                <td>{formatDateTime(s.end_time)}</td>
                                <td>{formatCurrency(s.opening_balance)}</td>
                                <td>{s.closing_balance != null ? formatCurrency(s.closing_balance) : '-'}</td>
                                <td style={{ color: s.variance && s.variance !== 0 ? (s.variance > 0 ? 'green' : 'red') : 'inherit' }}>
                                    {s.variance != null ? formatCurrency(s.variance) : '-'}
                                </td>
                                <td><span className={`badge badge-${s.status === 'open' ? 'success' : 'secondary'}`}>{s.status === 'open' ? 'مفتوحة' : 'مغلقة'}</span></td>
                                <td>
                                    <button className="btn btn-sm btn-info" onClick={() => loadReconciliation(s.id)} title="تقرير التسوية">
                                        <i className="fas fa-file-alt"></i>
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {shifts.length === 0 && <tr><td colSpan="8" style={{ textAlign: 'center' }}>لا توجد ورديات</td></tr>}
                    </tbody>
                </table>
            </div>

            {/* Open Shift Modal */}
            {showOpenModal && (
                <div className="modal-overlay" onClick={() => setShowOpenModal(false)}>
                    <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: '400px' }}>
                        <div className="modal-header">
                            <h3>فتح وردية جديدة</h3>
                            <button className="close-btn" onClick={() => setShowOpenModal(false)}>&times;</button>
                        </div>
                        <div className="form-group">
                            <label>الرصيد الافتتاحي (ج.م)</label>
                            <input type="number" step="0.01" value={openingBalance} onChange={e => setOpeningBalance(e.target.value)} placeholder="0.00" />
                        </div>
                        <div className="modal-footer">
                            <button className="btn btn-secondary" onClick={() => setShowOpenModal(false)}>إلغاء</button>
                            <button className="btn btn-primary" onClick={handleOpenShift}>فتح الوردية</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Close Shift Modal */}
            {showCloseModal && (
                <div className="modal-overlay" onClick={() => setShowCloseModal(false)}>
                    <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: '400px' }}>
                        <div className="modal-header">
                            <h3>إغلاق الوردية</h3>
                            <button className="close-btn" onClick={() => setShowCloseModal(false)}>&times;</button>
                        </div>
                        <div className="form-group">
                            <label>الرصيد الختامي الفعلي (ج.م)</label>
                            <input type="number" step="0.01" value={closingBalance} onChange={e => setClosingBalance(e.target.value)} placeholder="0.00" />
                        </div>
                        <div className="form-group">
                            <label>ملاحظات</label>
                            <textarea value={closeNotes} onChange={e => setCloseNotes(e.target.value)} placeholder="ملاحظات اختيارية" />
                        </div>
                        <div className="modal-footer">
                            <button className="btn btn-secondary" onClick={() => setShowCloseModal(false)}>إلغاء</button>
                            <button className="btn btn-danger" onClick={handleCloseShift}>إغلاق الوردية</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Drawer Log Modal */}
            {showDrawerModal && (
                <div className="modal-overlay" onClick={() => setShowDrawerModal(false)}>
                    <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: '400px' }}>
                        <div className="modal-header">
                            <h3>حركة درج النقدية</h3>
                            <button className="close-btn" onClick={() => setShowDrawerModal(false)}>&times;</button>
                        </div>
                        <div className="form-group">
                            <label>نوع الحركة</label>
                            <select value={drawerForm.action} onChange={e => setDrawerForm(prev => ({ ...prev, action: e.target.value }))}>
                                <option value="cash_in">إيداع</option>
                                <option value="cash_out">سحب</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label>المبلغ</label>
                            <input type="number" step="0.01" value={drawerForm.amount} onChange={e => setDrawerForm(prev => ({ ...prev, amount: e.target.value }))} />
                        </div>
                        <div className="form-group">
                            <label>السبب</label>
                            <input type="text" value={drawerForm.reason} onChange={e => setDrawerForm(prev => ({ ...prev, reason: e.target.value }))} />
                        </div>
                        <div className="modal-footer">
                            <button className="btn btn-secondary" onClick={() => setShowDrawerModal(false)}>إلغاء</button>
                            <button className="btn btn-primary" onClick={handleDrawerLog}>تسجيل</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Reconciliation Modal */}
            {showReconciliation && reconciliationData && (
                <div className="modal-overlay" onClick={() => setShowReconciliation(null)}>
                    <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: '500px' }}>
                        <div className="modal-header">
                            <h3>تقرير تسوية الوردية #{showReconciliation}</h3>
                            <button className="close-btn" onClick={() => setShowReconciliation(null)}>&times;</button>
                        </div>
                        <div style={{ padding: '16px' }}>
                            <div className="stats-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
                                <div className="stat-card">
                                    <h4>الرصيد الافتتاحي</h4>
                                    <p>{formatCurrency(reconciliationData.shift?.opening_balance)}</p>
                                </div>
                                <div className="stat-card">
                                    <h4>الرصيد المتوقع</h4>
                                    <p>{formatCurrency(reconciliationData.shift?.expected_balance)}</p>
                                </div>
                                <div className="stat-card">
                                    <h4>الرصيد الفعلي</h4>
                                    <p>{formatCurrency(reconciliationData.shift?.closing_balance)}</p>
                                </div>
                                <div className="stat-card">
                                    <h4>الفرق</h4>
                                    <p style={{ color: reconciliationData.shift?.variance != 0 ? 'red' : 'green' }}>
                                        {formatCurrency(reconciliationData.shift?.variance)}
                                    </p>
                                </div>
                            </div>
                            {reconciliationData.payment_breakdown && (
                                <div style={{ marginTop: '16px' }}>
                                    <h4>توزيع طرق الدفع</h4>
                                    <table>
                                        <thead><tr><th>الطريقة</th><th>العدد</th><th>الإجمالي</th></tr></thead>
                                        <tbody>
                                            {reconciliationData.payment_breakdown.map((pb, i) => (
                                                <tr key={i}>
                                                    <td>{pb.method}</td>
                                                    <td>{pb.count}</td>
                                                    <td>{formatCurrency(pb.total)}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                        <div className="modal-footer">
                            <button className="btn btn-secondary" onClick={() => setShowReconciliation(null)}>إغلاق</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default ShiftManagement
