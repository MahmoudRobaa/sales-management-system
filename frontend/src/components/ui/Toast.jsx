import { useState, useCallback, createContext, useContext } from 'react'

const ToastContext = createContext(null)

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, variant = 'info', duration = 4000) => {
    const id = Date.now() + Math.random()
    setToasts(prev => [...prev, { id, message, variant }])
    if (duration > 0) {
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id))
      }, duration)
    }
    return id
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  const contextValue = {
    show: addToast,
    success: (msg, dur) => addToast(msg, 'success', dur),
    error: (msg, dur) => addToast(msg, 'danger', dur),
    warning: (msg, dur) => addToast(msg, 'warning', dur),
    info: (msg, dur) => addToast(msg, 'info', dur),
  }

  return (
    <ToastContext.Provider value={contextValue}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  )
}

const iconMap = {
  success: 'fas fa-check-circle',
  danger: 'fas fa-exclamation-circle',
  warning: 'fas fa-exclamation-triangle',
  info: 'fas fa-info-circle',
}

function ToastContainer({ toasts, onRemove }) {
  if (!toasts.length) return null

  return (
    <div className="ui-toast-container">
      {toasts.map(t => (
        <div key={t.id} className={`ui-toast ui-toast--${t.variant}`}>
          <i className={iconMap[t.variant] || iconMap.info} />
          <span className="ui-toast__message">{t.message}</span>
          <button className="ui-toast__close" onClick={() => onRemove(t.id)} aria-label="إغلاق">
            <i className="fas fa-times" />
          </button>
        </div>
      ))}
    </div>
  )
}
