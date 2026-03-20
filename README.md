# Eco-Agent

Full-stack energy monitoring dashboard with:
- FastAPI backend APIs
- React frontend dashboards
- Scheduler-driven email reporting

## Project Structure
- `backend/api` - FastAPI APIs
- `backend/energy-dashboard` - data processing + scheduler/mail agents
- `frontend` - React + Vite UI

## Quick Start

### 1) Backend API
```powershell
cd backend/api
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2) Frontend
```powershell
cd frontend
npm install
npm run dev
```

## Environment Setup
A demo template is provided at `.env.example`.

1. Copy `.env.example` to `.env`
2. Fill your own SMTP/API values
3. Never commit real secrets

## Notes
- Scheduler email features depend on valid SMTP credentials.
- Default frontend API base URL can be overridden via `VITE_API_URL`.
