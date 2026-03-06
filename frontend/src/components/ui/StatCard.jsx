const colorMap = {
  primary: { bg: 'var(--color-primary-light)', icon: 'var(--color-primary)', text: 'var(--color-primary-dark)' },
  success: { bg: 'var(--color-success-light)', icon: 'var(--color-success)', text: 'var(--color-success-dark)' },
  warning: { bg: 'var(--color-warning-light)', icon: 'var(--color-warning)', text: 'var(--color-warning-dark)' },
  danger: { bg: 'var(--color-danger-light)', icon: 'var(--color-danger)', text: 'var(--color-danger-dark)' },
  info: { bg: 'var(--color-info-light)', icon: 'var(--color-info)', text: 'var(--color-info-dark)' },
}

export default function StatCard({ title, value, icon, color = 'primary', subtitle, trend, className = '' }) {
  const colors = colorMap[color] || colorMap.primary

  return (
    <div className={`ui-stat-card ${className}`}>
      <div className="ui-stat-card__icon" style={{ backgroundColor: colors.bg, color: colors.icon }}>
        <i className={icon} />
      </div>
      <div className="ui-stat-card__content">
        <span className="ui-stat-card__title">{title}</span>
        <span className="ui-stat-card__value tabular-nums">{value}</span>
        {subtitle && <span className="ui-stat-card__subtitle">{subtitle}</span>}
        {trend !== undefined && (
          <span className={`ui-stat-card__trend ${trend >= 0 ? 'ui-stat-card__trend--up' : 'ui-stat-card__trend--down'}`}>
            <i className={`fas fa-arrow-${trend >= 0 ? 'up' : 'down'}`} />
            {Math.abs(trend)}%
          </span>
        )}
      </div>
    </div>
  )
}
