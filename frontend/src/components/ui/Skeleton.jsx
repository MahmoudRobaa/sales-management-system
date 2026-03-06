export default function Skeleton({ width, height = 16, circle = false, className = '', count = 1 }) {
  const style = {
    width: circle ? height : width,
    height,
    borderRadius: circle ? '50%' : 'var(--radius-sm)',
  }

  if (count === 1) {
    return <span className={`ui-skeleton ${className}`} style={style} />
  }

  return (
    <div className="ui-skeleton-group">
      {Array.from({ length: count }).map((_, i) => (
        <span key={i} className={`ui-skeleton ${className}`} style={style} />
      ))}
    </div>
  )
}

export function SkeletonCard() {
  return (
    <div className="ui-skeleton-card">
      <Skeleton width="40%" height={14} />
      <Skeleton width="60%" height={24} />
      <Skeleton width="30%" height={12} />
    </div>
  )
}
