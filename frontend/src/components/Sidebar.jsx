export default function Sidebar({ view, onNavigate, userEmail, onLogout }) {
  return (
    <div className="sidebar">
      <div className="brand">
        support<span>/</span>console
      </div>

      <button
        className={`nav-item ${view === 'queue' ? 'active' : ''}`}
        onClick={() => onNavigate('queue')}
      >
        Queue
      </button>
      <button
        className={`nav-item ${view === 'new' ? 'active' : ''}`}
        onClick={() => onNavigate('new')}
      >
        New ticket
      </button>

      <div className="sidebar-footer">
        {userEmail && <div className="sidebar-user">{userEmail}</div>}
        <button className="nav-item" onClick={onLogout}>
          Sign out
        </button>
      </div>
    </div>
  )
}
