export default function Table({ columns, data, onSort, sortField, sortDir, loading, emptyMessage = 'لا توجد بيانات', className = '' }) {
  if (loading) return <TableSkeleton columns={columns.length} />

  return (
    <div className={`ui-table-wrapper ${className}`}>
      <table className="ui-table">
        <thead>
          <tr>
            {columns.map(col => (
              <th
                key={col.key}
                className={col.sortable ? 'ui-table__th--sortable' : ''}
                style={col.width ? { width: col.width } : undefined}
                onClick={() => col.sortable && onSort?.(col.key)}
              >
                <span>{col.label}</span>
                {col.sortable && sortField === col.key && (
                  <i className={`fas fa-sort-${sortDir === 'asc' ? 'up' : 'down'} ui-table__sort-icon`} />
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="ui-table__empty">
                <i className="fas fa-inbox" />
                <span>{emptyMessage}</span>
              </td>
            </tr>
          ) : (
            data.map((row, i) => (
              <tr key={row.id ?? i}>
                {columns.map(col => (
                  <td key={col.key}>
                    {col.render ? col.render(row[col.key], row, i) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

function TableSkeleton({ columns = 5, rows = 5 }) {
  return (
    <div className="ui-table-wrapper">
      <table className="ui-table">
        <thead>
          <tr>
            {Array.from({ length: columns }).map((_, i) => (
              <th key={i}><span className="ui-skeleton" style={{ width: '60%', height: 14 }} /></th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: rows }).map((_, r) => (
            <tr key={r}>
              {Array.from({ length: columns }).map((_, c) => (
                <td key={c}><span className="ui-skeleton" style={{ width: `${60 + Math.random() * 30}%`, height: 14 }} /></td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export { TableSkeleton }
