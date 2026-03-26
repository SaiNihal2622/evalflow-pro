# EvalFlow Pro – API Documentation

Base URL: `http://localhost:8000` (dev) or your Railway deployment URL.

## Authentication

All endpoints accept an optional `Authorization: Bearer <token>` header. In dev mode (default token), auth is bypassed.

---

## Endpoints

### POST /api/evaluate

Evaluate a single prompt-response pair.

**Request:**
```json
{
  "prompt": "What is the capital of France?",
  "response": "The capital of France is Paris."
}
```

**Response:**
```json
{
  "id": 1,
  "prompt": "What is the capital of France?",
  "response": "The capital of France is Paris.",
  "accuracy": "correct",
  "issues": [],
  "confidence": 0.95,
  "severity": "low",
  "llm_score": 0.95,
  "rule_score": 1.0,
  "final_score": 0.97,
  "latency_ms": 1250,
  "created_at": "2026-03-26T18:00:00"
}
```

---

### POST /api/batch-evaluate

Evaluate multiple pairs in batch (max 100).

**Request:**
```json
{
  "evaluations": [
    { "prompt": "...", "response": "..." },
    { "prompt": "...", "response": "..." }
  ]
}
```

**Response:** Array of `EvaluationResult` objects.

---

### GET /api/evaluations

Paginated list with filters.

**Query Parameters:**
| Param     | Type   | Default | Description                    |
|-----------|--------|---------|--------------------------------|
| page      | int    | 1       | Page number                    |
| page_size | int    | 20      | Items per page (max 100)       |
| accuracy  | string | —       | Filter: `correct`, `incorrect` |
| severity  | string | —       | Filter: `low`, `medium`, `high`|
| search    | string | —       | Search in prompt/response text |

---

### GET /api/evaluations/{id}

Get single evaluation by ID.

### DELETE /api/evaluations/{id}

Delete single evaluation.

---

### GET /api/stats

Dashboard statistics: totals, accuracy rate, averages, distributions, recent evaluations.

### GET /api/analytics/trends?days=30

Time-series data: daily totals, correct/incorrect counts, avg confidence.

### GET /api/analytics/issues

Issue type distribution with counts and percentages.

---

### GET /api/export/json

Download all evaluations as JSON file.

### GET /api/export/csv

Download all evaluations as CSV file.

Both support optional `accuracy` and `severity` query filters.

---

### GET /health

Health check endpoint.

**Response:** `{ "status": "healthy" }`
