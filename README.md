# Azure AI Foundry Agent Web App (Python)

This repository is a **fork** of `microsoft-foundry/foundry-agent-webapp` (branch `main`), adapted to be a **runnable Python example**.

## What changed vs upstream

- **Backend rewritten**: **.NET → Python (FastAPI)**.
- **Auth simplified**: replaced Entra ID / MSAL with a **simple username/password login** that returns a **JWT**.
- **Deployment moved to legacy**: the original `azd`/Bicep/deployment automation has been moved under `legacy/`.

## Project layout

- `backend/`: FastAPI API (chat streaming + agent metadata) and JWT auth
- `frontend/`: React + Vite chat UI (calls `/api/*`)
- `legacy/`: original upstream-style deployment + .NET backend (kept for reference)

## Local run (dev)

### Backend (FastAPI)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create `backend/.env`:

```env
# Simple auth
AUTH_USERNAME=demo
AUTH_PASSWORD_HASH=$2b$12$...
JWT_SECRET_KEY=change-me

# Azure AI Foundry Agent
AI_AGENT_ENDPOINT=https://<your-project>.services.ai.azure.com
AI_AGENT_ID=<your-agent-id>

# Optional
ENVIRONMENT=development
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Generate `AUTH_PASSWORD_HASH` (bcrypt):

```bash
python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('your_password'))"
```

Start the API (matches the frontend dev proxy):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

### Frontend (Vite)

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Notes

- The frontend logs in via `POST /api/auth/login` and stores the JWT in `localStorage`.
- Anything under `legacy/` is **not maintained** here; it is kept to document the original template and deployment approach.

