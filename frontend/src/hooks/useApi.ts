import { useState, useEffect, useCallback } from 'react';
import { api, type StatsResponse, type PaginatedEvaluations, type EvaluationResult, type TrendsResponse, type IssueDistributionResponse } from '../lib/api';

// ─── useStats ────────────────────────────────────────────────────

export function useStats() {
  const [data, setData] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const stats = await api.getStats();
      setData(stats);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load stats');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refetch(); }, [refetch]);

  return { data, loading, error, refetch };
}

// ─── useEvaluations ──────────────────────────────────────────────

export function useEvaluations(params: {
  page?: number;
  page_size?: number;
  accuracy?: string;
  severity?: string;
  search?: string;
} = {}) {
  const [data, setData] = useState<PaginatedEvaluations | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.getEvaluations(params);
      setData(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load evaluations');
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => { refetch(); }, [refetch]);

  return { data, loading, error, refetch };
}

// ─── useEvaluate ─────────────────────────────────────────────────

export function useEvaluate() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const evaluate = useCallback(async (prompt: string, response: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.evaluate(prompt, response);
      setResult(res);
      return res;
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Evaluation failed';
      setError(msg);
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  return { evaluate, result, loading, error };
}

// ─── useTrends ───────────────────────────────────────────────────

export function useTrends(days = 30) {
  const [data, setData] = useState<TrendsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.getTrends(days);
      setData(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load trends');
    } finally {
      setLoading(false);
    }
  }, [days]);

  useEffect(() => { refetch(); }, [refetch]);

  return { data, loading, error, refetch };
}

// ─── useIssueDistribution ────────────────────────────────────────

export function useIssueDistribution() {
  const [data, setData] = useState<IssueDistributionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.getIssueDistribution();
      setData(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load issue distribution');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refetch(); }, [refetch]);

  return { data, loading, error, refetch };
}
