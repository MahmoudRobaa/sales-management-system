import { useState, useEffect } from 'react'
import { SettingsAPI } from '../services/api'

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

    useEffect(() => {
        loadSettings()
    }, [])

    const loadSettings = async () => {
        try {
            setLoading(true)
            const data = await SettingsAPI.getAll()
            const settingsObj = {}
            data.forEach(s => {
                settingsObj[s.key] = s.value || ''
            })
            setSettings({
                store_name: settingsObj.store_name || '',
                store_address: settingsObj.store_address || '',
                store_phone: settingsObj.store_phone || '',
                min_stock_alert: settingsObj.min_stock_alert || '5',
                vat_rate: settingsObj.vat_rate || '15'
            })
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

    if (loading) {
        return <div className="loading"><div className="loading-spinner"></div><span>جاري التحميل...</span></div>
    }

    return (
        <>
            <div className="page-header">
                <h1>الإعدادات</h1>
            </div>

            <div className="card">
                <div className="card-header">
                    <h2>إعدادات المحل</h2>
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
        </>
    )
}

export default Settings
