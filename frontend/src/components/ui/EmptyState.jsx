export default function EmptyState({ icon = 'fas fa-inbox', title = 'لا توجد بيانات', description, action, className = '' }) {
  return (
    <div className={`ui-empty ${className}`}>
      <div className="ui-empty__icon">
        <i className={icon} />
      </div>
      <h3 className="ui-empty__title">{title}</h3>
      {description && <p className="ui-empty__desc">{description}</p>}
      {action && <div className="ui-empty__action">{action}</div>}
    </div>
  )
}
