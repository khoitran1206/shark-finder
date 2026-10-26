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
backend/    FastAPI app: main.py (wiring), app/routers/ (endpoints), app/services/ (Whisper + Gemini),
            app/match.py (scoring), app/auth.py (Cognito token check), app/models/, tests/, migrations, scripts
frontend/   React + Vite + Tailwind; auth via AWS Amplify (Cognito)
docker-compose.yml   runs both services
```

## ⚙️ Configuration

| Setting | Where | Default / notes |
| --- | --- | --- |
| `DATABASE_URL` | `backend/.env` | Postgres URL. Unset = local SQLite at `backend/app/dev.db` |
| `GEMINI_API_KEY` | `backend/.env` | Secret. Required for firm recordings; read on first use, so the app starts without it |
| `GEMINI_MODEL` | `backend/.env` | `gemini-2.5-flash` |
| `WHISPER_SIZE` | `backend/.env` | `small`. The model loads on the first recording (slow once) |
| `CORS_ORIGINS` | `backend/.env` | Comma-separated. `http://localhost:5173,http://127.0.0.1:5173` |
| `COGNITO_REGION`, `COGNITO_USER_POOL_ID`, `COGNITO_CLIENT_ID` | `backend/.env` | Public IDs used to verify login tokens. Default to the current pool |
| `VITE_API_URL` | `frontend/.env` | Backend URL. `http://127.0.0.1:8000/` |
| `VITE_COGNITO_USER_POOL_ID`, `VITE_COGNITO_CLIENT_ID` | `frontend/.env` | Must match the backend `COGNITO_*` values. Default to the current pool |

All settings are optional except the Gemini key. Only `GEMINI_API_KEY` and a Postgres `DATABASE_URL` are secrets; the Cognito IDs are public.
Backend code reads everything through `backend/app/config.py`.

Secrets live only in `backend/.env` (git-ignored). Start from the templates:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env   # optional
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
