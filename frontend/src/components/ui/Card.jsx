export default function Card({ children, className = '', padding = true, ...props }) {
  return (
    <div className={`ui-card ${padding ? '' : 'ui-card--no-pad'} ${className}`} {...props}>
      {children}
    </div>
  )
}

export function CardHeader({ title, subtitle, action, icon, className = '' }) {
  return (
    <div className={`ui-card__header ${className}`}>
      <div className="ui-card__header-text">
        {icon && <i className={`ui-card__header-icon ${icon}`} />}
        <div>
          <h3 className="ui-card__title">{title}</h3>
          {subtitle && <p className="ui-card__subtitle">{subtitle}</p>}
        </div>
      </div>
      {action && <div className="ui-card__header-action">{action}</div>}
    </div>
  )
}

export function CardBody({ children, className = '' }) {
  return <div className={`ui-card__body ${className}`}>{children}</div>
}

export function CardFooter({ children, className = '' }) {
  return <div className={`ui-card__footer ${className}`}>{children}</div>
}
