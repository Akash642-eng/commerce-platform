import { useEffect, useState } from 'react'
import { getToken, clearToken, me } from './api'
import Sidebar from './components/Sidebar'
import SignalStrip, { SignalLegend } from './components/SignalStrip'
import Login from './pages/Login'
import Queue from './pages/Queue'
import NewTicket from './pages/NewTicket'
import TicketDetail from './pages/TicketDetail'

const VIEW_TITLES = {
  queue: 'Ticket queue',
  new: 'New ticket',
  detail: 'Ticket',
}

export default function App() {
  const [checkingSession, setCheckingSession] = useState(true)
  const [userEmail, setUserEmail] = useState(null)
  const [view, setView] = useState('queue')
  const [selectedTicketId, setSelectedTicketId] = useState(null)
  const [tickets, setTickets] = useState([])

  // On load, if a token is already stored, confirm it's still valid before
  // dropping the user straight into the queue.
  useEffect(() => {
    const token = getToken()
    if (!token) {
      setCheckingSession(false)
      return
    }
    me()
      .then((res) => setUserEmail(res?.user?.user_id || 'agent'))
      .catch(() => clearToken())
      .finally(() => setCheckingSession(false))
  }, [])

  function handleSignedIn(email) {
    setUserEmail(email)
    setView('queue')
  }

  function handleLogout() {
    clearToken()
    setUserEmail(null)
    setTickets([])
    setView('queue')
  }

  function handleNavigate(next) {
    setSelectedTicketId(null)
    setView(next)
  }

  function handleOpenTicket(id) {
    setSelectedTicketId(id)
    setView('detail')
  }

  function handleTicketCreated(id) {
    setSelectedTicketId(id)
    setView('detail')
  }

  if (checkingSession) {
    return <div className="empty-state">Loading console…</div>
  }

  if (!userEmail) {
    return <Login onSignedIn={handleSignedIn} />
  }

  return (
    <div className="app-shell">
      <Sidebar
        view={view}
        onNavigate={handleNavigate}
        userEmail={userEmail}
        onLogout={handleLogout}
      />

      <div className="topbar">
        <div className="topbar-title">
          {view === 'detail' && selectedTicketId
            ? `TCK-${String(selectedTicketId).padStart(6, '0')}`
            : VIEW_TITLES[view]}
        </div>
        <div className="topbar-meta">{tickets.length} ticket{tickets.length === 1 ? '' : 's'} in queue</div>
      </div>

      <SignalStrip tickets={tickets} />
      <SignalLegend tickets={tickets} />

      <div className="main">
        {view === 'queue' && (
          <Queue onOpenTicket={handleOpenTicket} onTicketsLoaded={setTickets} />
        )}
        {view === 'new' && <NewTicket onCreated={handleTicketCreated} />}
        {view === 'detail' && selectedTicketId && (
          <TicketDetail
            ticketId={selectedTicketId}
            userEmail={userEmail}
            onBack={() => handleNavigate('queue')}
          />
        )}
      </div>
    </div>
  )
}
