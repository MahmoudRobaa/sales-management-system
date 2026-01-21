import { useState, useEffect } from 'react'
import { DashboardAPI, ProductsAPI, CustomersAPI, SuppliersAPI, SalesAPI, PurchasesAPI, SettingsAPI } from './services/api'
import Dashboard from './components/Dashboard'
import Products from './components/Products'
import Customers from './components/Customers'
import Suppliers from './components/Suppliers'
import Sales from './components/Sales'
import Purchases from './components/Purchases'
import Inventory from './components/Inventory'
import Settings from './components/Settings'
import Reports from './components/Reports'
import Login from './components/Login'
import './index.css'

function App() {
  const [activeSection, setActiveSection] = useState('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  // Check for existing login on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('user')
    const token = localStorage.getItem('token')
    
    if (savedUser && token) {
      try {
        setUser(JSON.parse(savedUser))
      } catch (e) {
        localStorage.removeItem('user')
        localStorage.removeItem('token')
      }
    }
    setIsLoading(false)
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
  }

  const handleLogout = () => {
    // Call logout endpoint
    fetch('/api/auth/logout', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    }).catch(() => {})
    
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    setUser(null)
  }

  const menuItems = [
    { id: 'dashboard', icon: 'fas fa-tachometer-alt', label: 'لوحة التحكم' },
    { id: 'products', icon: 'fas fa-boxes', label: 'كارتة الأصناف' },
    { id: 'sales', icon: 'fas fa-shopping-cart', label: 'المبيعات' },
    { id: 'purchases', icon: 'fas fa-shopping-bag', label: 'المشتريات' },
    { id: 'reports', icon: 'fas fa-chart-bar', label: 'التقارير' },
    { id: 'inventory', icon: 'fas fa-warehouse', label: 'المخازن' },
    { id: 'customers', icon: 'fas fa-users', label: 'العملاء' },
    { id: 'suppliers', icon: 'fas fa-truck', label: 'الموردين' },
    { id: 'settings', icon: 'fas fa-cog', label: 'الإعدادات' },
  ]

  // Add user management for admin
  if (user && user.role === 'admin') {
    menuItems.push({ id: 'users', icon: 'fas fa-user-shield', label: 'إدارة المستخدمين' })
  }

  const renderSection = () => {
    switch (activeSection) {
      case 'dashboard': return <Dashboard />
      case 'products': return <Products />
      case 'customers': return <Customers />
      case 'suppliers': return <Suppliers />
      case 'sales': return <Sales user={user} />
      case 'purchases': return <Purchases user={user} />
      case 'inventory': return <Inventory />
      case 'settings': return <Settings />
      case 'reports': return <Reports />
      case 'users': return <UserManagement />
      default: return <Dashboard />
    }
  }

  // Show loading spinner while checking auth
  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div className="spinner"></div>
      </div>
    )
  }

  // Show login if not authenticated
  if (!user) {
    return <Login onLogin={handleLogin} />
  }

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="logo">
          <h2>نظام إدارة المبيعات</h2>
          <p>محل الحاسوب والأدوات الكهربائية</p>
        </div>

        <div className="menu">
          {menuItems.map(item => (
            <div
              key={item.id}
              className={`menu-item ${activeSection === item.id ? 'active' : ''}`}
              onClick={() => {
                setActiveSection(item.id)
                setSidebarOpen(false)
              }}
            >
              <i className={item.icon}></i>
              <span>{item.label}</span>
            </div>
          ))}
        </div>

        {/* User Info & Logout */}
        <div className="user-section">
          <div className="user-info">
            <i className="fas fa-user-circle"></i>
            <div>
              <span className="user-name">{user.full_name}</span>
              <span className="user-role">
                {user.role === 'admin' ? 'مدير' : user.role === 'manager' ? 'مشرف' : 'كاشير'}
              </span>
            </div>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            <i className="fas fa-sign-out-alt"></i>
            تسجيل الخروج
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {renderSection()}
      </div>
    </div>
  )
}

// User Management Component (for admin)
function UserManagement() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingUser, setEditingUser] = useState(null)
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    full_name: '',
    role: 'cashier'
  })

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      const response = await fetch('/api/users', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setUsers(data)
      }
    } catch (error) {
      console.error('Error fetching users:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const url = editingUser ? `/api/users/${editingUser.id}` : '/api/users'
    const method = editingUser ? 'PUT' : 'POST'
    
    try {
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
      })
      
      if (response.ok) {
        fetchUsers()
        setShowModal(false)
        setEditingUser(null)
        setFormData({ username: '', password: '', full_name: '', role: 'cashier' })
      }
    } catch (error) {
      console.error('Error saving user:', error)
    }
  }

  const handleDelete = async (userId) => {
    if (!window.confirm('هل أنت متأكد من حذف هذا المستخدم؟')) return
    
    try {
      await fetch(`/api/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      fetchUsers()
    } catch (error) {
      console.error('Error deleting user:', error)
    }
  }

  const openEdit = (user) => {
    setEditingUser(user)
    setFormData({
      username: user.username,
      password: '',
      full_name: user.full_name,
      role: user.role
    })
    setShowModal(true)
  }

  if (loading) return <div className="loading">جاري التحميل...</div>

  return (
    <div className="section-content">
      <div className="section-header">
        <h2>إدارة المستخدمين</h2>
        <button className="btn btn-primary" onClick={() => { setEditingUser(null); setFormData({ username: '', password: '', full_name: '', role: 'cashier' }); setShowModal(true) }}>
          <i className="fas fa-plus"></i> إضافة مستخدم
        </button>
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th>اسم المستخدم</th>
            <th>الاسم الكامل</th>
            <th>الدور</th>
            <th>الحالة</th>
            <th>آخر دخول</th>
            <th>الإجراءات</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.id}>
              <td>{user.username}</td>
              <td>{user.full_name}</td>
              <td>
                <span className={`badge ${user.role === 'admin' ? 'badge-danger' : user.role === 'manager' ? 'badge-warning' : 'badge-info'}`}>
                  {user.role === 'admin' ? 'مدير' : user.role === 'manager' ? 'مشرف' : 'كاشير'}
                </span>
              </td>
              <td>
                <span className={`badge ${user.is_active ? 'badge-success' : 'badge-secondary'}`}>
                  {user.is_active ? 'نشط' : 'معطل'}
                </span>
              </td>
              <td>{user.last_login ? new Date(user.last_login).toLocaleString('ar-EG') : '-'}</td>
              <td>
                <button className="btn btn-sm btn-info" onClick={() => openEdit(user)}>
                  <i className="fas fa-edit"></i>
                </button>
                {user.username !== 'admin' && (
                  <button className="btn btn-sm btn-danger" onClick={() => handleDelete(user.id)}>
                    <i className="fas fa-trash"></i>
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>{editingUser ? 'تعديل مستخدم' : 'إضافة مستخدم جديد'}</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>اسم المستخدم</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={e => setFormData({...formData, username: e.target.value})}
                  required
                  disabled={editingUser}
                />
              </div>
              <div className="form-group">
                <label>كلمة المرور {editingUser && '(اتركه فارغاً للإبقاء)'}</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={e => setFormData({...formData, password: e.target.value})}
                  required={!editingUser}
                />
              </div>
              <div className="form-group">
                <label>الاسم الكامل</label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={e => setFormData({...formData, full_name: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>الدور</label>
                <select
                  value={formData.role}
                  onChange={e => setFormData({...formData, role: e.target.value})}
                >
                  <option value="cashier">كاشير</option>
                  <option value="manager">مشرف</option>
                  <option value="admin">مدير</option>
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>إلغاء</button>
                <button type="submit" className="btn btn-primary">حفظ</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
