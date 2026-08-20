const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'

const TOKEN_KEY = 'support_console_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

async function request(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' }

  if (auth) {
    const token = getToken()
    if (!token) throw new ApiError('Not signed in', 401)
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  let data = null
  try {
    data = await res.json()
  } catch {
    // empty/non-JSON body
  }

  if (!res.ok) {
    const detail = data?.detail || data?.message || `Request failed (${res.status})`
    throw new ApiError(detail, res.status)
  }

  return data
}

// --- Auth (routed through gateway's /auth passthrough — no token verification on this path) ---

export function login(email, password) {
  return request('/auth/login', {
    method: 'POST',
    body: { email, password },
    auth: false,
  })
}

export function me() {
  return request('/auth/me')
}

// --- Support tickets (routed through gateway's /support passthrough — token required) ---

export function listTickets() {
  return request('/support/tickets')
}

export function getTicket(ticketId) {
  return request(`/support/ticket/${ticketId}`)
}

export function createTicket({ user_id, subject, description }) {
  return request('/support/ticket', {
    method: 'POST',
    body: { user_id, subject, description },
  })
}

export function updateTicketStatus(ticketId, status) {
  return request(`/support/ticket/${ticketId}/status`, {
    method: 'PUT',
    body: { status },
  })
}

export function getTicketMessages(ticketId) {
  return request(`/support/ticket/${ticketId}/messages`)
}

export function addMessage({ ticket_id, sender_id, message }) {
  return request('/support/message', {
    method: 'POST',
    body: { ticket_id, sender_id, message },
  })
}

export { ApiError }
