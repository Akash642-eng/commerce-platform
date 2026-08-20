import { useState } from 'react'
import { createTicket } from '../api'

export default function NewTicket({ onCreated }) {
  const [userId, setUserId] = useState('')
  const [subject, setSubject] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const ticket = await createTicket({
        user_id: userId,
        subject,
        description,
      })
      onCreated(ticket.id)
    } catch (err) {
      setError(err.message || 'Could not create the ticket')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ maxWidth: 520 }}>
      <div className="queue-header">
        <h1>New ticket</h1>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <form className="panel" onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="userId">Customer user ID</label>
          <input
            id="userId"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="e.g. usr_4821"
            required
          />
        </div>
        <div className="field">
          <label htmlFor="subject">Subject</label>
          <input
            id="subject"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="What's the issue about?"
            required
          />
        </div>
        <div className="field">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Details the customer provided…"
            required
          />
        </div>
        <button className="btn" type="submit" disabled={submitting}>
          {submitting ? 'Creating…' : 'Create ticket'}
        </button>
      </form>
    </div>
  )
}
