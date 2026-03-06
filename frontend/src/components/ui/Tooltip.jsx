import { useState, useRef, useEffect } from 'react'

export default function Tooltip({ children, content, position = 'top', className = '' }) {
  const [visible, setVisible] = useState(false)
  const triggerRef = useRef(null)

  if (!content) return children

  return (
    <span
      className={`ui-tooltip-wrapper ${className}`}
      ref={triggerRef}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      onFocus={() => setVisible(true)}
      onBlur={() => setVisible(false)}
    >
      {children}
      {visible && (
        <span className={`ui-tooltip ui-tooltip--${position}`} role="tooltip">
          {content}
        </span>
      )}
    </span>
  )
}
