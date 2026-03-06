import { forwardRef } from 'react'

const Input = forwardRef(({
  label,
  error,
  hint,
  icon,
  type = 'text',
  size = 'md',
  fullWidth = true,
  className = '',
  ...props
}, ref) => {
  const sizeClass = size === 'sm' ? 'ui-input--sm' : size === 'lg' ? 'ui-input--lg' : ''

  return (
    <div className={`ui-field ${fullWidth ? 'ui-field--full' : ''} ${className}`}>
      {label && <label className="ui-field__label">{label}</label>}
      <div className={`ui-input-wrapper ${error ? 'ui-input-wrapper--error' : ''} ${sizeClass}`}>
        {icon && <i className={`ui-input__icon ${icon}`} />}
        <input
          ref={ref}
          type={type}
          className="ui-input"
          {...props}
        />
      </div>
      {error && <span className="ui-field__error">{error}</span>}
      {hint && !error && <span className="ui-field__hint">{hint}</span>}
    </div>
  )
})

Input.displayName = 'Input'

export function Textarea({ label, error, hint, rows = 3, className = '', ...props }) {
  return (
    <div className={`ui-field ui-field--full ${className}`}>
      {label && <label className="ui-field__label">{label}</label>}
      <textarea
        className={`ui-input ui-textarea ${error ? 'ui-input--error' : ''}`}
        rows={rows}
        {...props}
      />
      {error && <span className="ui-field__error">{error}</span>}
      {hint && !error && <span className="ui-field__hint">{hint}</span>}
    </div>
  )
}

export default Input
