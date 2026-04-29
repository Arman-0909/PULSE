# PULSE — API Monitoring System

> Real-time API health monitoring with WebSocket live updates, JWT auth, and PostgreSQL support.

![Dashboard](docs/dashboard.png)

---

## Features

### Real-time Monitoring

- **WebSocket Live Updates** — Dashboard receives metric pushes instantly, no polling
- **Automated Health Checks** — Pings all services every 30s (configurable via env)
- **Uptime Tracking** — Calculates uptime % from historical metrics
- **Response Time Sparklines** — SVG charts from real data
- **Live Indicator** — Green "Live" badge when WebSocket is connected, auto-reconnects

### Authentication

- **Sign Up / Sign In** — Tabbed login page, real user accounts stored in DB
- **bcrypt Hashed Passwords** — No plaintext, uses `bcrypt.hashpw()` + salt
- **JWT Sessions** — `python-jose` HS256 tokens in httponly cookies (24h expiry)
- **Protected Admin** — All admin/CRUD routes require valid JWT
- **Public Pages** — Dashboard and home are accessible without login

### Admin Panel (Full CRUD)

- **Add Services** — Name, URL, group, duplicate detection, auto `https://` prefix
- **Edit Services** — Modal with pre-filled fields, inline update
- **Delete Services** — Confirmation modal, cascades metric deletion
- **Service Groups** — Create and assign groups
- **Toast Notifications** — Success/error feedback on every action

### Production Ready

- **PostgreSQL Support** — Switch from SQLite to PostgreSQL via env var
- **Environment Variables** — All secrets in `.env`, nothing hardcoded
- **CORS Middleware** — Ready for API consumers
- **Structured Logging** — Timestamped logs for all operations
- **REST API** — Full JSON API + Swagger docs at `/docs`

---

## Screenshots

### Login (Sign In / Sign Up)
![Login](docs/login.png)

### Admin Panel
![Admin](docs/admin.png)

### Dashboard (WebSocket Live)
![Dashboard](docs/dashboard.png)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI + Python 3.11+ |
| **Database** | SQLite (dev) / PostgreSQL (prod) via SQLModel |
| **Real-time** | WebSocket (FastAPI native + websockets lib) |
| **Auth** | bcrypt + JWT (python-jose) |
| **Scheduler** | APScheduler (async) |
| **HTTP Client** | HTTPX (async) |
| **Config** | python-dotenv (.env files) |
| **Icons** | Lucide Icons (CDN) |
| **Font** | Inter (Google Fonts) |

---

## Project Structure

```
PULSE/
├── app/
│   ├── main.py                # FastAPI app + lifespan + CORS
│   ├── api/
│   │   └── routes.py          # Pages + REST API + WebSocket + Auth
│   ├── core/
│   │   ├── config.py          # Reads from .env (no hardcoded secrets)
│   │   ├── auth.py            # bcrypt hashing + JWT create/decode
│   │   └── websocket.py       # WebSocket connection manager
│   ├── db/
│   │   ├── database.py        # Engine (SQLite or PostgreSQL)
│   │   └── models.py          # User, Service, ServiceGroup, Metric
│   ├── scheduler/
│   │   └── jobs.py            # APScheduler health check jobs
│   ├── services/
│   │   └── monitor.py         # HTTP checker + WS broadcaster
│   ├── templates/
│   │   ├── index.html         # Home page
│   │   ├── dashboard.html     # Live dashboard (WebSocket)
│   │   ├── admin.html         # Admin (CRUD + modals)
│   │   └── login.html         # Sign In / Sign Up
│   └── utils/
│       └── logger.py          # Structured logging
├── .env                       # Local config (git-ignored)
├── .env.example               # Template for new deployments
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

```bash
# Clone
git clone <repo-url> && cd PULSE

# Virtual environment
python -m venv env
env\Scripts\activate         # Windows
source env/bin/activate      # macOS/Linux

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env         # Edit .env with your values

# Run
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000** — Sign up — Start monitoring.

---

## Environment Variables

```env
# Database (SQLite for dev, PostgreSQL for prod)
DATABASE_URL=sqlite:///./pulse.db
# DATABASE_URL=postgresql://user:pass@localhost:5432/pulse

# Auth (CHANGE THESE IN PRODUCTION)
SECRET_KEY=your-random-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# Monitoring
CHECK_INTERVAL=30
REQUEST_TIMEOUT=5
```

---

## Routes

| Route | Auth | Description |
|-------|------|------------|
| `/` | Public | Home page |
| `/dashboard` | Public | Live dashboard (WebSocket) |
| `/login` | Public | Sign In / Sign Up |
| `/admin` | JWT | Admin panel (CRUD) |
| `/logout` | - | Clear session |
| `/docs` | Public | Swagger API docs |
| `/ws` | - | WebSocket endpoint |

---

## REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/services` | All services + metrics |
| `GET` | `/api/stats` | Global stats |
| `GET` | `/api/services/{id}/metrics` | Metric history |
| `GET` | `/api/groups` | All groups |
| `DELETE` | `/api/services/{id}` | Delete service |
| `WS` | `/ws` | Real-time metric stream |

---

## Requirements

```
fastapi, uvicorn, sqlmodel, httpx, jinja2, apscheduler,
python-multipart, websockets, bcrypt, python-jose[cryptography],
python-dotenv, psycopg2-binary
```

---

## License

MIT
