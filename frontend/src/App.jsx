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
import './index.css'

function App() {
  const [activeSection, setActiveSection] = useState('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(false)

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

  const renderSection = () => {
    switch (activeSection) {
      case 'dashboard': return <Dashboard />
      case 'products': return <Products />
      case 'customers': return <Customers />
      case 'suppliers': return <Suppliers />
      case 'sales': return <Sales />
      case 'purchases': return <Purchases />
      case 'inventory': return <Inventory />
      case 'settings': return <Settings />
      case 'reports': return <Reports />
      default: return <Dashboard />
    }
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
      </div>

      {/* Main Content */}
      <div className="main-content">
        {renderSection()}
      </div>
    </div>
  )
}

export default App
