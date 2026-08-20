const LABELS = {
  OPEN: 'Open',
  IN_PROGRESS: 'In progress',
  RESOLVED: 'Resolved',
  CLOSED: 'Closed',
}

export default function StatusBadge({ status }) {
  const key = (status || 'OPEN').toLowerCase()
  const label = LABELS[status] || status

  return (
    <span className={`status-badge status-${key}`}>
      <span className="dot" style={{ background: 'currentColor' }} />
      {label}
    </span>
  )
}
