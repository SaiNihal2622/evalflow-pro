import { useState } from 'react';
import { Download, Trash2, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { AccuracyBadge, SeverityBadge } from '../components/Badge';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { ErrorState } from '../components/EmptyState';
import { useEvaluations } from '../hooks/useApi';
import { api, downloadBlob } from '../lib/api';

export default function DatasetExplorer() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [accuracy, setAccuracy] = useState('');
  const [severity, setSeverity] = useState('');

  const { data, loading, error, refetch } = useEvaluations({
    page, page_size: 15,
    accuracy: accuracy || undefined,
    severity: severity || undefined,
    search: search || undefined,
  });

  const handleSearch = (e: React.FormEvent) => { e.preventDefault(); setSearch(searchInput); setPage(1); };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete?')) return;
    try { await api.deleteEvaluation(id); refetch(); } catch { alert('Failed'); }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-[22px] font-bold text-white">Dataset</h1>
          <p className="text-surface-600 text-[13px] mt-1">Browse and export evaluation data</p>
        </div>
        <div className="flex gap-2">
          <button onClick={async () => { try { downloadBlob(await api.exportJSON(), 'evalflow.json'); } catch { /* */ } }} className="btn-secondary text-[12px]">
            <Download className="w-3.5 h-3.5" /> JSON
          </button>
          <button onClick={async () => { try { downloadBlob(await api.exportCSV(), 'evalflow.csv'); } catch { /* */ } }} className="btn-primary text-[12px]">
            <Download className="w-3.5 h-3.5" /> CSV
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-2">
        <form onSubmit={handleSearch} className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-700" />
          <input value={searchInput} onChange={(e) => setSearchInput(e.target.value)} placeholder="Search..." className="input pl-9" />
        </form>
        <select value={accuracy} onChange={(e) => { setAccuracy(e.target.value); setPage(1); }} className="input w-auto min-w-[120px]">
          <option value="">All Accuracy</option>
          <option value="correct">Correct</option>
          <option value="incorrect">Incorrect</option>
        </select>
        <select value={severity} onChange={(e) => { setSeverity(e.target.value); setPage(1); }} className="input w-auto min-w-[120px]">
          <option value="">All Severity</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      {loading ? <LoadingSpinner /> : error ? <ErrorState message={error} onRetry={refetch} /> : !data || data.items.length === 0 ? <EmptyState title="No results" description="Adjust filters or run evaluations." /> : (
        <>
          <div className="card overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#1a1a1a]">
                  {['ID', 'Prompt', 'Accuracy', 'Issues', 'Score', 'Severity', 'Date', ''].map(h => (
                    <th key={h} className="px-4 py-2.5 text-left text-[10px] font-semibold text-surface-600 uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.items.map((e) => (
                  <tr key={e.id} className="border-b border-[#111] hover:bg-[#111] transition-colors group">
                    <td className="px-4 py-3 text-[11px] text-surface-700 font-mono">#{e.id}</td>
                    <td className="px-4 py-3 text-[12px] text-surface-400 max-w-[200px] truncate">{e.prompt}</td>
                    <td className="px-4 py-3"><AccuracyBadge accuracy={e.accuracy} /></td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1">
                        {e.issues.length > 0 ? e.issues.slice(0, 2).map((issue, i) => (
                          <span key={i} className="px-1.5 py-0.5 text-[9px] font-medium rounded bg-red-500/5 text-red-400 border border-red-500/10">{issue}</span>
                        )) : <span className="text-[10px] text-surface-700">—</span>}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-[12px] font-semibold text-surface-300">{e.final_score != null ? (e.final_score * 100).toFixed(0) + '%' : '—'}</td>
                    <td className="px-4 py-3"><SeverityBadge severity={e.severity} /></td>
                    <td className="px-4 py-3 text-[10px] text-surface-700">{e.created_at ? new Date(e.created_at).toLocaleDateString() : '—'}</td>
                    <td className="px-4 py-3">
                      <button onClick={() => handleDelete(e.id)} className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-500/5 text-surface-800 hover:text-red-400 transition-all">
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex items-center justify-between text-[12px]">
            <span className="text-surface-600">{((data.page - 1) * data.page_size) + 1}–{Math.min(data.page * data.page_size, data.total)} of {data.total}</span>
            <div className="flex items-center gap-1">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={data.page <= 1} className="btn-secondary p-2 disabled:opacity-20"><ChevronLeft className="w-3.5 h-3.5" /></button>
              <span className="text-surface-500 px-2 font-mono">{data.page}/{data.total_pages}</span>
              <button onClick={() => setPage(p => Math.min(data.total_pages, p + 1))} disabled={data.page >= data.total_pages} className="btn-secondary p-2 disabled:opacity-20"><ChevronRight className="w-3.5 h-3.5" /></button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
