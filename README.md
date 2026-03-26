# EvalFlow Pro – AI Evaluation & Data Quality Engine

A production-grade platform for evaluating LLM responses with structured metrics, detecting hallucinations, and managing evaluation datasets.

## Architecture

```
User → React Dashboard → FastAPI API
    → LLM Evaluation Engine → Rule Engine
    → PostgreSQL → Response Formatter → UI
```

## Tech Stack

| Layer     | Technology                       |
|-----------|----------------------------------|
| Backend   | FastAPI, SQLAlchemy, Python 3.11 |
| Database  | PostgreSQL (prod) / SQLite (dev) |
| AI Layer  | OpenAI / Google Gemini           |
| Frontend  | React, TypeScript, Tailwind CSS  |
| Charts    | Recharts                         |
| Deploy    | Railway (backend), Vercel (frontend) |

## Quick Start

### Backend

```bash
cd backend
cp .env.example .env
# Edit .env with your API keys
pip install -r requirements.txt
python main.py
```

Server starts at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard at `http://localhost:5173`.

## Project Structure

```
backend/
├── main.py              # FastAPI entry point
├── config.py            # Environment configuration
├── db/
│   └── database.py      # Async SQLAlchemy setup
├── models/
│   └── evaluation.py    # DB model + Pydantic schemas
├── llm/
│   ├── base.py          # Abstract LLM provider
│   ├── openai_provider.py
│   ├── gemini_provider.py
│   └── factory.py       # Provider factory
├── routes/
│   ├── auth.py          # Bearer token auth
│   ├── evaluate.py      # Evaluation CRUD
│   ├── stats.py         # Analytics endpoints
│   └── export.py        # JSON/CSV export
├── services/
│   ├── rule_engine.py   # Deterministic validation
│   ├── evaluation.py    # Orchestration service
│   └── analytics.py     # Aggregation queries
├── Dockerfile
└── railway.toml

frontend/
├── src/
│   ├── App.tsx           # Root layout + routing
│   ├── lib/api.ts        # Typed API client
│   ├── hooks/useApi.ts   # React hooks
│   ├── components/       # Reusable UI components
│   └── pages/            # Dashboard, Evaluate, Dataset, Analytics
├── index.html
└── vite.config.ts
```

## Features

- **LLM Evaluation**: Automated evaluation using OpenAI/Gemini with structured JSON output
- **Rule Engine**: Deterministic hallucination, contradiction, completeness, and vagueness detection
- **Combined Scoring**: Weighted LLM (60%) + Rules (40%) for robust evaluation
- **Dataset Management**: Store, browse, filter, search, and export (JSON/CSV) all evaluations
- **Analytics**: Accuracy distribution, issue frequency, time-series trends, confidence tracking
- **Batch Processing**: Evaluate up to 100 items with concurrency control
- **Authentication**: Bearer token authentication
- **Modern UI**: Glassmorphic dark theme with smooth animations and Recharts visualizations
