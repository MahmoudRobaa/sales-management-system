export default function SearchInput({ value, onChange, placeholder = 'بحث...', className = '', ...props }) {
  return (
    <div className={`ui-search ${className}`}>
      <i className="fas fa-search ui-search__icon" />
      <input
        type="search"
        className="ui-search__input"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        {...props}
      />
      {value && (
        <button
          type="button"
          className="ui-search__clear"
          onClick={() => onChange({ target: { value: '' } })}
          aria-label="مسح البحث"
        >
          <i className="fas fa-times" />
        </button>
      )}
    </div>
  )
}
