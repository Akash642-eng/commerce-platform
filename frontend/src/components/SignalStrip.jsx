const STATUS_COLORS = {
  OPEN: 'var(--status-open)',
  IN_PROGRESS: 'var(--status-in_progress)',
  RESOLVED: 'var(--status-resolved)',
  CLOSED: 'var(--status-closed)',
}

const STATUS_ORDER = ['OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED']

// Renders one tick per ticket, ordered oldest-to-newest left-to-right, colored
// by status — a queue heartbeat you can read without opening the table.
export default function SignalStrip({ tickets }) {
  if (!tickets || tickets.length === 0) {
    return (
      <div className="signal-strip">
        <div className="signal-tick" style={{ background: 'var(--border)' }} />
      </div>
    )
  }

  return (
    <div className="signal-strip">
      {tickets.map((t) => (
        <div
          key={t.id}
          className="signal-tick"
          style={{ background: STATUS_COLORS[t.status] || 'var(--border)' }}
          title={`#${t.id} — ${t.status}`}
        />
      ))}
    </div>
  )
}

export function SignalLegend({ tickets }) {
  const counts = STATUS_ORDER.reduce((acc, s) => {
    acc[s] = (tickets || []).filter((t) => t.status === s).length
    return acc
  }, {})

  return (
    <div className="signal-legend">
      {STATUS_ORDER.map((s) => (
        <span key={s}>
          <span className="legend-dot" style={{ background: STATUS_COLORS[s] }} />
          {s.replace('_', ' ').toLowerCase()} · {counts[s]}
        </span>
      ))}
    </div>
  )
}
