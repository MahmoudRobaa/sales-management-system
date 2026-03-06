import { useEffect, useCallback } from 'react'

export default function Modal({
  open,
  onClose,
  title,
  children,
  footer,
  size = 'md',
  className = '',
}) {
  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Escape') onClose?.()
  }, [onClose])

  useEffect(() => {
    if (open) {
      document.addEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = ''
    }
  }, [open, handleKeyDown])

  if (!open) return null

  const sizeClass = size === 'sm' ? 'ui-modal--sm' : size === 'lg' ? 'ui-modal--lg' : size === 'xl' ? 'ui-modal--xl' : ''

  return (
    <div className="ui-modal-overlay" onClick={onClose}>
      <div
        className={`ui-modal ${sizeClass} ${className}`}
        onClick={e => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <div className="ui-modal__header">
          <h3 className="ui-modal__title">{title}</h3>
          <button className="ui-modal__close" onClick={onClose} aria-label="إغلاق">
            <i className="fas fa-times" />
          </button>
        </div>
        <div className="ui-modal__body">
          {children}
        </div>
        {footer && (
          <div className="ui-modal__footer">
            {footer}
          </div>
        )}
      </div>
    </div>
  )
}

export function ConfirmModal({ open, onClose, onConfirm, title, message, confirmText = 'تأكيد', cancelText = 'إلغاء', variant = 'danger' }) {
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={title}
      size="sm"
      footer={
        <>
          <button className="ui-btn ui-btn--secondary ui-btn--md" onClick={onClose}>{cancelText}</button>
          <button className={`ui-btn ui-btn--${variant} ui-btn--md`} onClick={onConfirm}>{confirmText}</button>
        </>
      }
    >
      <p style={{ color: 'var(--color-text-secondary)', lineHeight: 'var(--line-height-relaxed)' }}>{message}</p>
    </Modal>
  )
}
