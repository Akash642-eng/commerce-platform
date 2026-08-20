import { useEffect, useState } from 'react'
import { getTicket, getTicketMessages, addMessage, updateTicketStatus } from '../api'
import StatusBadge from '../components/StatusBadge'

function formatTime(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function TicketDetail({ ticketId, userEmail, onBack }) {
  const [ticket, setTicket] = useState(null)
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [reply, setReply] = useState('')
  const [sending, setSending] = useState(false)
  const [updatingStatus, setUpdatingStatus] = useState(false)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const [t, m] = await Promise.all([getTicket(ticketId), getTicketMessages(ticketId)])
      setTicket(t)
      setMessages(m)
    } catch (err) {
      setError(err.message || 'Could not load this ticket')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ticketId])

  async function handleReply(e) {
    e.preventDefault()
    if (!reply.trim()) return
    setSending(true)
    try {
      await addMessage({
        ticket_id: ticketId,
        sender_id: userEmail || 'agent',
        message: reply.trim(),
      })
      setReply('')
      const m = await getTicketMessages(ticketId)
      setMessages(m)
    } catch (err) {
      setError(err.message || 'Could not send the reply')
    } finally {
      setSending(false)
    }
  }

  async function handleStatusChange(newStatus) {
    setUpdatingStatus(true)
    try {
      await updateTicketStatus(ticketId, newStatus)
      setTicket((prev) => ({ ...prev, status: newStatus }))
    } catch (err) {
      setError(err.message || 'Could not update status')
    } finally {
      setUpdatingStatus(false)
    }
  }

  if (loading) return <div className="empty-state">Loading ticket…</div>

  return (
    <div style={{ maxWidth: 720 }}>
      <button className="back-link" onClick={onBack}>
        ← Back to queue
      </button>

      {error && <div className="error-banner">{error}</div>}

      {ticket && (
        <>
          <div className="detail-header">
            <div>
              <h1>{ticket.subject}</h1>
              <div className="detail-meta">
                TCK-{String(ticket.id).padStart(6, '0')} · opened by {ticket.user_id} ·{' '}
                {formatTime(ticket.created_at)}
              </div>
            </div>
            <StatusBadge status={ticket.status} />
          </div>

          <div className="panel">
            <h2>Description</h2>
            <div className="message-body">{ticket.description}</div>
          </div>

          <div className="panel">
            <h2>Status</h2>
            <div className="status-select-row">
              <select
                value={ticket.status}
                disabled={updatingStatus}
                onChange={(e) => handleStatusChange(e.target.value)}
                style={{
                  background: 'var(--panel-raised)',
                  border: '1px solid var(--border)',
                  borderRadius: 3,
                  padding: '7px 10px',
                  color: 'var(--text)',
                }}
              >
                <option value="OPEN">Open</option>
                <option value="IN_PROGRESS">In progress</option>
                <option value="RESOLVED">Resolved</option>
                <option value="CLOSED">Closed</option>
              </select>
              {updatingStatus && <span className="detail-meta">Saving…</span>}
            </div>
          </div>

          <div className="panel">
            <h2>Messages</h2>
            {messages.length === 0 ? (
              <div className="empty-state" style={{ padding: '20px 0' }}>
                No messages yet — reply below to start the thread.
              </div>
            ) : (
              messages.map((m) => (
                <div className="message-item" key={m.id}>
                  <div className="message-sender">
                    {m.sender_id}
                    <span className="message-time">{formatTime(m.created_at)}</span>
                  </div>
                  <div className="message-body">{m.message}</div>
                </div>
              ))
            )}

            <form onSubmit={handleReply} style={{ marginTop: 16 }}>
              <div className="field">
                <label htmlFor="reply">Reply</label>
                <textarea
                  id="reply"
                  value={reply}
                  onChange={(e) => setReply(e.target.value)}
                  placeholder="Write a reply to the customer…"
                />
              </div>
              <button className="btn" type="submit" disabled={sending || !reply.trim()}>
                {sending ? 'Sending…' : 'Send reply'}
              </button>
            </form>
          </div>
        </>
      )}
    </div>
  )
}
