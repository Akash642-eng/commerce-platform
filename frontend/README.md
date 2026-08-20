# Support Console

Internal ops UI for the support-service — agents triage the ticket queue, work threads, and change ticket status. Talks to the backend exclusively through the api-gateway (never directly to support-service), so gateway auth/rate-limiting/tracing all apply.

## Run it

1. `cp .env.example .env` and point `VITE_API_BASE_URL` at your gateway (default assumes `docker-compose up` with the gateway on `:8080`).
2. `npm install`
3. `npm run dev` → http://localhost:5173

## Sign in

Hits `POST /auth/login` through the gateway. auth-service's login accepts any non-empty email/password (there's no user lookup yet — it just mints a token), so use any email/password to get in during local testing.

## What's wired up

- **Queue** — `GET /support/tickets`, filterable by status
- **Ticket detail** — `GET /support/ticket/{id}` + `/messages`, reply via `POST /support/message`, status change via `PUT /support/ticket/{id}/status`
- **New ticket** — `POST /support/ticket`
- **Signal strip** — one tick per ticket colored by status, a queue heartbeat you can read without opening the table

## Known gaps

- auth-service's `/auth/login` doesn't verify credentials against a user record yet — anyone can get a token. Don't point this at anything but local/dev until that's fixed.
- No pagination on `/support/tickets` — fine for dev/demo, will need it once ticket volume grows.
