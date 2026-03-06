export default function Pagination({ current, total, pageSize, onChange, className = '' }) {
  const totalPages = Math.ceil(total / pageSize)
  if (totalPages <= 1) return null

  const getPages = () => {
    const pages = []
    const delta = 1

    for (let i = 1; i <= totalPages; i++) {
      if (i === 1 || i === totalPages || (i >= current - delta && i <= current + delta)) {
        pages.push(i)
      } else if (pages[pages.length - 1] !== '...') {
        pages.push('...')
      }
    }
    return pages
  }

  const start = (current - 1) * pageSize + 1
  const end = Math.min(current * pageSize, total)

  return (
    <div className={`ui-pagination ${className}`}>
      <span className="ui-pagination__info">
        عرض {start}-{end} من {total}
      </span>
      <div className="ui-pagination__controls">
        <button
          className="ui-pagination__btn"
          disabled={current <= 1}
          onClick={() => onChange(current - 1)}
          aria-label="الصفحة السابقة"
        >
          <i className="fas fa-chevron-right" />
        </button>
        {getPages().map((page, i) =>
          page === '...' ? (
            <span key={`dots-${i}`} className="ui-pagination__dots">...</span>
          ) : (
            <button
              key={page}
              className={`ui-pagination__btn ${page === current ? 'ui-pagination__btn--active' : ''}`}
              onClick={() => onChange(page)}
            >
              {page}
            </button>
          )
        )}
        <button
          className="ui-pagination__btn"
          disabled={current >= totalPages}
          onClick={() => onChange(current + 1)}
          aria-label="الصفحة التالية"
        >
          <i className="fas fa-chevron-left" />
        </button>
      </div>
    </div>
  )
}
