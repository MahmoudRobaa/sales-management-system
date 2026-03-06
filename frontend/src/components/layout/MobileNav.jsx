export default function MobileNav({ open, menuItems, activeSection, onNavigate, onClose }) {
  if (!open) return null

  return (
    <>
      <div className="ui-mobile-overlay" onClick={onClose} />
      <nav className="ui-mobile-nav">
        <div className="ui-mobile-nav__header">
          <h3>القائمة</h3>
          <button className="ui-mobile-nav__close" onClick={onClose} aria-label="إغلاق">
            <i className="fas fa-times" />
          </button>
        </div>
        <div className="ui-mobile-nav__items">
          {menuItems.map(item => (
            <button
              key={item.id}
              className={`ui-mobile-nav__item ${activeSection === item.id ? 'ui-mobile-nav__item--active' : ''}`}
              onClick={() => {
                onNavigate(item.id)
                onClose()
              }}
            >
              <i className={item.icon} />
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      </nav>
    </>
  )
}
