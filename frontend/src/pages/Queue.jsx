import { useEffect, useState } from 'react'
import { listTickets } from '../api'
import StatusBadge from '../components/StatusBadge'

function formatTime(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function Queue({ onOpenTicket, onTicketsLoaded }) {
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [search, setSearch] = useState('')

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const data = await listTickets()
      setTickets(data)
      onTicketsLoaded?.(data)
    } catch (err) {
      setError(err.message || 'Could not load the queue')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const byStatus =
    statusFilter === 'ALL' ? tickets : tickets.filter((t) => t.status === statusFilter)

  const q = search.trim().toLowerCase()
  const visible = !q
    ? byStatus
    : byStatus.filter((t) => {
        const ticketRef = `tck-${String(t.id).padStart(6, '0')}`
        return (
          ticketRef.includes(q) ||
          String(t.id).includes(q) ||
          t.subject?.toLowerCase().includes(q) ||
          t.user_id?.toLowerCase().includes(q) ||
          t.description?.toLowerCase().includes(q)
        )
      })

  return (
    <div>
      <div className="queue-header">
        <h1>Ticket queue</h1>
        <div style={{ display: 'flex', gap: 10 }}>
          <input
            type="text"
            placeholder="Search ID, subject, customer…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              background: 'var(--panel-raised)',
              border: '1px solid var(--border)',
              borderRadius: 3,
              padding: '6px 10px',
              color: 'var(--text)',
              minWidth: 220,
            }}
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{
              background: 'var(--panel-raised)',
              border: '1px solid var(--border)',
              borderRadius: 3,
              padding: '6px 10px',
              color: 'var(--text)',
            }}
          >
            <option value="ALL">All statuses</option>
            <option value="OPEN">Open</option>
            <option value="IN_PROGRESS">In progress</option>
            <option value="RESOLVED">Resolved</option>
            <option value="CLOSED">Closed</option>
          </select>
          <button className="btn-ghost btn" onClick={load}>
            Refresh
          </button>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {loading ? (
        <div className="empty-state">Loading queue…</div>
      ) : visible.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-title">No tickets here</div>
          {q
            ? `Nothing matches "${search}".`
            : statusFilter === 'ALL'
            ? 'New tickets from customers will show up in this queue.'
            : `No tickets are currently ${statusFilter.replace('_', ' ').toLowerCase()}.`}
        </div>
      ) : (
        <table className="ticket-table">
          <thead>
            <tr>
              <th style={{ width: 90 }}>ID</th>
              <th>Subject</th>
              <th style={{ width: 140 }}>Customer</th>
              <th style={{ width: 140 }}>Status</th>
              <th style={{ width: 140 }}>Opened</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((t) => (
              <tr key={t.id} onClick={() => onOpenTicket(t.id)}>
                <td className="ticket-id">TCK-{String(t.id).padStart(6, '0')}</td>
                <td className="ticket-subject">{t.subject}</td>
                <td className="ticket-user">{t.user_id}</td>
                <td>
                  <StatusBadge status={t.status} />
                </td>
                <td className="ticket-time">{formatTime(t.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
