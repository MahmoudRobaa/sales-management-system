import { useEffect } from 'react'

export default function Drawer({ open, onClose, title, children, footer, position = 'start', size = 'md' }) {
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [open])

  if (!open) return null

  const sizeClass = size === 'sm' ? 'ui-drawer--sm' : size === 'lg' ? 'ui-drawer--lg' : ''
  const posClass = position === 'end' ? 'ui-drawer--end' : 'ui-drawer--start'

  return (
    <div className="ui-drawer-overlay" onClick={onClose}>
      <div
        className={`ui-drawer ${posClass} ${sizeClass}`}
        onClick={e => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <div className="ui-drawer__header">
          <h3 className="ui-drawer__title">{title}</h3>
          <button className="ui-drawer__close" onClick={onClose} aria-label="إغلاق">
            <i className="fas fa-times" />
          </button>
        </div>
        <div className="ui-drawer__body">
          {children}
        </div>
        {footer && (
          <div className="ui-drawer__footer">
            {footer}
          </div>
        )}
      </div>
    </div>
  )
}
