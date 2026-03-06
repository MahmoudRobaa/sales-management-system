import { forwardRef } from 'react'

const variants = {
  primary: 'ui-btn--primary',
  secondary: 'ui-btn--secondary',
  danger: 'ui-btn--danger',
  success: 'ui-btn--success',
  ghost: 'ui-btn--ghost',
  outline: 'ui-btn--outline',
}

const sizes = {
  sm: 'ui-btn--sm',
  md: 'ui-btn--md',
  lg: 'ui-btn--lg',
}

const Button = forwardRef(({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  iconPosition = 'start',
  loading = false,
  disabled = false,
  fullWidth = false,
  className = '',
  ...props
}, ref) => {
  const classes = [
    'ui-btn',
    variants[variant],
    sizes[size],
    fullWidth && 'ui-btn--full',
    loading && 'ui-btn--loading',
    className,
  ].filter(Boolean).join(' ')

  return (
    <button
      ref={ref}
      className={classes}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <i className="fas fa-spinner fa-spin" />}
      {!loading && icon && iconPosition === 'start' && <i className={icon} />}
      {children && <span>{children}</span>}
      {!loading && icon && iconPosition === 'end' && <i className={icon} />}
    </button>
  )
})

Button.displayName = 'Button'

export function IconButton({ icon, label, variant = 'ghost', size = 'md', className = '', ...props }) {
  return (
    <button
      className={`ui-icon-btn ${variants[variant]} ${sizes[size]} ${className}`}
      aria-label={label}
      title={label}
      {...props}
    >
      <i className={icon} />
    </button>
  )
}

export default Button
