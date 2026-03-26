const API_BASE = import.meta.env.VITE_API_URL || '';

interface RequestOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {} } = options;

  const config: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  const token = localStorage.getItem('evalflow_token');
  if (token) {
    (config.headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `Request failed: ${response.status}`);
  }

  // Handle blob responses for CSV/JSON export
  const contentType = response.headers.get('content-type');
  if (contentType?.includes('text/csv') || (contentType?.includes('application/json') && response.headers.get('content-disposition'))) {
    return response.blob() as unknown as T;
  }

  return response.json();
}

// ─── Types ───────────────────────────────────────────────────────

export interface EvaluationResult {
  id: number;
  prompt: string;
  response: string;
  accuracy: string;
  issues: string[];
  confidence: number;
  severity: string;
  llm_score: number | null;
  rule_score: number | null;
  final_score: number | null;
  latency_ms: number | null;
  created_at: string | null;
}

export interface PaginatedEvaluations {
  items: EvaluationResult[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface StatsResponse {
  total_evaluations: number;
  correct_count: number;
  incorrect_count: number;
  accuracy_rate: number;
  avg_confidence: number;
  avg_final_score: number;
  issue_distribution: Record<string, number>;
  severity_distribution: Record<string, number>;
  recent_evaluations: EvaluationResult[];
}

export interface TrendDataPoint {
  date: string;
  total: number;
  correct: number;
  incorrect: number;
  avg_confidence: number;
}

export interface TrendsResponse {
  trends: TrendDataPoint[];
}

export interface IssueItem {
  issue: string;
  count: number;
  percentage: number;
}

export interface IssueDistributionResponse {
  issues: IssueItem[];
  total_issues: number;
}

// ─── API Functions ───────────────────────────────────────────────

export const api = {
  // Evaluate
  evaluate: (prompt: string, response: string) =>
    request<EvaluationResult>('/api/evaluate', {
      method: 'POST',
      body: { prompt, response },
    }),

  batchEvaluate: (evaluations: { prompt: string; response: string }[]) =>
    request<EvaluationResult[]>('/api/batch-evaluate', {
      method: 'POST',
      body: { evaluations },
    }),

  // Evaluations
  getEvaluations: (params: {
    page?: number;
    page_size?: number;
    accuracy?: string;
    severity?: string;
    search?: string;
  } = {}) => {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.set(key, String(value));
      }
    });
    return request<PaginatedEvaluations>(`/api/evaluations?${searchParams}`);
  },

  getEvaluation: (id: number) =>
    request<EvaluationResult>(`/api/evaluations/${id}`),

  deleteEvaluation: (id: number) =>
    request<{ message: string }>(`/api/evaluations/${id}`, { method: 'DELETE' }),

  // Stats & Analytics
  getStats: () => request<StatsResponse>('/api/stats'),

  getTrends: (days = 30) =>
    request<TrendsResponse>(`/api/analytics/trends?days=${days}`),

  getIssueDistribution: () =>
    request<IssueDistributionResponse>('/api/analytics/issues'),

  // Export
  exportJSON: () => {
    const token = localStorage.getItem('evalflow_token');
    const headers: Record<string, string> = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return fetch(`${API_BASE}/api/export/json`, { headers }).then(r => r.blob());
  },

  exportCSV: () => {
    const token = localStorage.getItem('evalflow_token');
    const headers: Record<string, string> = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return fetch(`${API_BASE}/api/export/csv`, { headers }).then(r => r.blob());
  },
};

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
