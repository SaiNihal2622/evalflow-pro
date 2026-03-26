# EvalFlow Pro – Deployment Guide

## Backend Deployment (Railway)

### 1. Create Railway Project

1. Go to [railway.app](https://railway.app) and create a new project
2. Add a **PostgreSQL** database service
3. Add a new **service** from your GitHub repo (select the `backend/` directory as root)

### 2. Configure Environment Variables

In Railway service settings, add these env vars:

```
DATABASE_URL=<Railway provides this automatically from PostgreSQL>
OPENAI_API_KEY=sk-your-key-here
LLM_PROVIDER=openai
AUTH_TOKEN=your-secure-production-token
CORS_ORIGINS=https://your-frontend-domain.vercel.app
PORT=8000
```

> **Note:** Railway auto-injects `DATABASE_URL` if you link the PostgreSQL service. Make sure to change it to use `postgresql+asyncpg://` prefix instead of `postgresql://`.

### 3. Deploy

Railway auto-deploys on push. The `railway.toml` and `Dockerfile` handle the build.

Health check: `GET /health` confirms the service is running.

---

## Frontend Deployment (Vercel)

### 1. Create Vercel Project

1. Go to [vercel.com](https://vercel.com) and import your repo
2. Set **Root Directory** to `frontend`
3. Framework preset: **Vite**

### 2. Configure Environment Variables

In Vercel project settings:

```
VITE_API_URL=https://your-backend.up.railway.app
```

### 3. Deploy

Vercel auto-deploys on push. Build command: `npm run build`, output dir: `dist`.

---

## Environment Variables Reference

| Variable        | Required | Default              | Description                     |
|-----------------|----------|----------------------|---------------------------------|
| DATABASE_URL    | Yes      | sqlite (dev)         | PostgreSQL connection string    |
| OPENAI_API_KEY  | No*      | —                    | OpenAI API key                  |
| GEMINI_API_KEY  | No*      | —                    | Google Gemini API key           |
| LLM_PROVIDER    | No       | openai               | `openai` or `gemini`            |
| AUTH_TOKEN       | No       | evalflow-dev-token   | API auth token                  |
| CORS_ORIGINS    | No       | localhost:5173,3000  | Comma-separated allowed origins |
| PORT            | No       | 8000                 | Server port                     |

*At least one LLM API key is needed for LLM evaluation. Without it, the system runs in rules-only mode.
