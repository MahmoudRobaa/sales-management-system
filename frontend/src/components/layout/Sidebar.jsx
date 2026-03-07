import { useState, useEffect } from 'react'

export default function Sidebar({ menuItems, activeSection, onNavigate, user, onLogout, onCollapse }) {
  const [collapsed, setCollapsed] = useState(false)

  useEffect(() => {
    onCollapse?.(collapsed)
  }, [collapsed])

  return (
    <aside className={`ui-sidebar ${collapsed ? 'ui-sidebar--collapsed' : ''}`}>
      {/* Logo */}
      <div className="ui-sidebar__logo">
        <div className="ui-sidebar__logo-icon">
          <i className="fas fa-store" />
        </div>
        {!collapsed && (
          <div className="ui-sidebar__logo-text">
            <h2>نظام المبيعات</h2>
            <p>إدارة شاملة</p>
          </div>
        )}
      </div>

      {/* Toggle */}
      <button
        className="ui-sidebar__toggle"
        onClick={() => setCollapsed(!collapsed)}
        aria-label={collapsed ? 'توسيع القائمة' : 'طي القائمة'}
      >
        <i className={`fas fa-chevron-${collapsed ? 'left' : 'right'}`} />
      </button>

      {/* Navigation */}
      <nav className="ui-sidebar__nav">
        {menuItems.map(item => (
          <button
            key={item.id}
            className={`ui-sidebar__item ${activeSection === item.id ? 'ui-sidebar__item--active' : ''}`}
            onClick={() => onNavigate(item.id)}
            title={collapsed ? item.label : undefined}
          >
            <i className={item.icon} />
            {!collapsed && <span>{item.label}</span>}
          </button>
        ))}
      </nav>

      {/* User Section */}
      <div className="ui-sidebar__user">
        <div className="ui-sidebar__user-info">
          <div className="ui-sidebar__avatar">
            <i className="fas fa-user" />
          </div>
          {!collapsed && (
            <div className="ui-sidebar__user-text">
              <span className="ui-sidebar__user-name">{user?.full_name}</span>
              <span className="ui-sidebar__user-role">
                {user?.role === 'admin' ? 'مدير' : user?.role === 'manager' ? 'مشرف' : 'كاشير'}
              </span>
            </div>
          )}
        </div>
        <button
          className="ui-sidebar__logout"
          onClick={onLogout}
          title="تسجيل الخروج"
        >
          <i className="fas fa-sign-out-alt" />
          {!collapsed && <span>خروج</span>}
        </button>
      </div>
    </aside>
  )
}
