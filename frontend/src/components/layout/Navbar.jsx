export default function Navbar({ title, breadcrumb, actions, onToggleMobile }) {
  return (
    <header className="ui-navbar">
      <div className="ui-navbar__right">
        <button className="ui-navbar__mobile-toggle" onClick={onToggleMobile} aria-label="القائمة">
          <i className="fas fa-bars" />
        </button>
        <div className="ui-navbar__titles">
          {breadcrumb && (
            <nav className="ui-breadcrumb" aria-label="مسار التنقل">
              {breadcrumb.map((item, i) => (
                <span key={i} className="ui-breadcrumb__item">
                  {i > 0 && <i className="fas fa-chevron-left ui-breadcrumb__sep" />}
                  {item.onClick ? (
                    <button className="ui-breadcrumb__link" onClick={item.onClick}>{item.label}</button>
                  ) : (
                    <span className="ui-breadcrumb__current">{item.label}</span>
                  )}
                </span>
              ))}
            </nav>
          )}
          <h1 className="ui-navbar__title">{title}</h1>
        </div>
      </div>
      {actions && <div className="ui-navbar__actions">{actions}</div>}
    </header>
  )
}
