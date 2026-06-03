# ⚡ VaultX

> Secure Cloud Storage & Smart File-Sharing Platform

![Version](https://img.shields.io/badge/version-1.0.0-purple)
![Status](https://img.shields.io/badge/status-active-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## What is VaultX?

VaultX is a full-stack secure cloud storage platform where users 
can upload, organize, preview, and share files using QR codes 
and secure links with permission controls.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, SQLAlchemy (async) |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| Storage | MinIO (local) → Cloudflare R2 (production) |
| Auth | JWT, bcrypt, Google OAuth2, TOTP 2FA |
| DevOps | Docker, Docker Compose, Nginx |

## Features

- 🔐 Secure authentication with JWT + 2FA
- 📁 File upload with drag-and-drop
- 📂 Nested folder organization
- 🔗 QR code file sharing
- 🔒 Password-protected share links
- 📊 Storage analytics dashboard
- 👁️ In-browser file preview
- 🗑️ Trash and restore system

## Quick Start

```bash
# Clone repository
git clone https://github.com/joelsmith-00/VaultX.git
cd VaultX

# Copy environment file
cp backend/.env.example backend/.env

# Start entire stack
docker-compose up -d

# Check health
curl http://localhost/api/health
```

## URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/api/docs |
| MinIO Console | http://localhost:9001 |
| Nginx Proxy | http://localhost |

## Project Structure
```

vaultx/
├── backend/          # Python FastAPI
│   ├── app/
│   │   ├── models/   # SQLAlchemy models
│   │   ├── routers/  # API route handlers
│   │   ├── services/ # Business logic
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── utils/    # Helper functions
│   │   └── middleware/
│   └── migrations/   # Alembic migrations
├── frontend/         # React TypeScript Vite
├── nginx/            # Reverse proxy
└── docker-compose.yml

```
## License

MIT © 2024 VaultX
