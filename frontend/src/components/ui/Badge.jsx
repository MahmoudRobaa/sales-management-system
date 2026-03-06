const variantMap = {
  default: 'ui-badge--default',
  primary: 'ui-badge--primary',
  success: 'ui-badge--success',
  warning: 'ui-badge--warning',
  danger: 'ui-badge--danger',
  info: 'ui-badge--info',
}

const sizeMap = {
  sm: 'ui-badge--sm',
  md: 'ui-badge--md',
}

export default function Badge({ children, variant = 'default', size = 'md', icon, dot = false, className = '', ...props }) {
  const classes = [
    'ui-badge',
    variantMap[variant],
    sizeMap[size],
    dot && 'ui-badge--dot',
    className,
  ].filter(Boolean).join(' ')

  return (
    <span className={classes} {...props}>
      {dot && <span className="ui-badge__dot" />}
      {icon && <i className={icon} />}
      {children}
    </span>
  )
}
