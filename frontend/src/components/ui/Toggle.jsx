export default function Toggle({ checked, onChange, label, disabled = false, className = '', ...props }) {
  return (
    <label className={`ui-toggle ${disabled ? 'ui-toggle--disabled' : ''} ${className}`}>
      <input
        type="checkbox"
        className="ui-toggle__input"
        checked={checked}
        onChange={onChange}
        disabled={disabled}
        {...props}
      />
      <span className="ui-toggle__track">
        <span className="ui-toggle__thumb" />
      </span>
      {label && <span className="ui-toggle__label">{label}</span>}
    </label>
  )
}
