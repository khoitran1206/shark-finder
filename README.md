# 🦈 Shark Finder

**Shark Finder** is a web application that connects **investors** and **startups/firms** through an **advanced AI-powered matching algorithm**.  
Our platform helps startups find the right investors for their stage, industry, and funding goals — while enabling investors to discover high-potential ventures that align with their portfolio interests.

---

## 🚀 Features

- 🤝 **Smart Matching Algorithm** — uses AI to connect investors with startups based on goals, sectors, and metrics
- 🧠 **AI-Driven Insights** — powered by **Google Gemini** and **faster-whisper** for intelligent recommendations and data analysis
- 💬 **Seamless Communication** — in-app chat and profile discovery for easy investor-founder interactions
- 📊 **Dynamic Dashboards** — visualize funding opportunities and connections in real time
- ☁️ **Scalable Backend** — built with FastAPI and Supabase for speed and reliability

---

## 🧰 Tech Stack

### Frontend

- **React.js** — modern, component-based UI
- **Tailwind CSS** — fast, responsive, utility-first styling

### Backend

- **FastAPI** — lightweight and high-performance Python framework
- **Supabase** — database, authentication, and storage
- **faster-whisper** — speech-to-text for the recorded pitch
- **Google Gemini API** — extracts structured firm details from the transcript

---

## 📁 Layout

```
backend/    FastAPI app (main.py), models + matching in app/, SQL migrations, dev scripts
frontend/   React + Vite + Tailwind; auth via AWS Amplify (Cognito)
docker-compose.yml   runs both services
```

## ⚙️ Configuration

| Setting | Where | Default / notes |
| --- | --- | --- |
| `DATABASE_URL` | `backend/.env` | Postgres URL. Unset = local SQLite at `backend/app/dev.db` |
| `GEMINI_API_KEY` | `backend/.env` | Required; backend won't start without it |
| Whisper model size | `backend/main.py` (`WHISPER_SIZE`) | `small`, hardcoded |
| CORS origins | `backend/main.py` | `localhost:5173` / `127.0.0.1:5173`, hardcoded |
| API base URL | `frontend/services/api-client.ts` | `http://127.0.0.1:8000/`, hardcoded |
| Cognito pool + client IDs | `frontend/src/main.tsx` | hardcoded; `frontend/amplify_outputs.json` is also imported by `frontend/src/amplify.ts` and is currently a stub |

Secrets live only in `backend/.env` (git-ignored). Start from the template:

```bash
cp backend/.env.example backend/.env
```

## ▶️ Run locally

Backend (needs `ffmpeg` installed):

```bash
cd backend && python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend:

```bash
cd frontend && npm ci && npm run dev
```

Or with Docker (reads `backend/.env`):

```bash
docker compose up --build
```

App: http://localhost:5173 · API: http://localhost:8000

## 🛠 Database scripts

- `backend/migrations/0001_investors_uuid_migration.sql` — converts `investors.id` from integer to UUID. **Postgres only; back up first.**
- `backend/scripts/reset_investors_table.py` — **drops and recreates all tables.** Development only.
