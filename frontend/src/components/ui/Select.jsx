import { forwardRef } from 'react'

const Select = forwardRef(({
  label,
  error,
  hint,
  options = [],
  placeholder,
  fullWidth = true,
  className = '',
  ...props
}, ref) => {
  return (
    <div className={`ui-field ${fullWidth ? 'ui-field--full' : ''} ${className}`}>
      {label && <label className="ui-field__label">{label}</label>}
      <div className={`ui-select-wrapper ${error ? 'ui-input-wrapper--error' : ''}`}>
        <select ref={ref} className="ui-select" {...props}>
          {placeholder && <option value="">{placeholder}</option>}
          {options.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        <i className="fas fa-chevron-down ui-select__arrow" />
      </div>
      {error && <span className="ui-field__error">{error}</span>}
      {hint && !error && <span className="ui-field__hint">{hint}</span>}
    </div>
  )
})

Select.displayName = 'Select'
export default Select
