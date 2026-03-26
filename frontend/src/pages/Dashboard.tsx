import { Activity, CheckCircle, TrendingUp, BarChart3 } from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import MetricCard from '../components/MetricCard';
import { AccuracyBadge, SeverityBadge } from '../components/Badge';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { ErrorState } from '../components/EmptyState';
import { useStats, useTrends } from '../hooks/useApi';

const tt = { backgroundColor: '#111', border: '1px solid #1a1a1a', borderRadius: '8px', fontSize: '12px' };

export default function Dashboard() {
  const { data: stats, loading, error, refetch } = useStats();
  const { data: trends } = useTrends(30);

  if (loading) return <LoadingSpinner message="Loading dashboard..." />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;
  if (!stats) return <EmptyState title="No data yet" description="Run your first evaluation to see metrics." />;

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-[22px] font-bold text-white">Dashboard</h1>
        <p className="text-surface-600 text-[13px] mt-1">Overview of your evaluation pipeline</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <MetricCard title="Evaluations" value={stats.total_evaluations} icon={<Activity className="w-5 h-5" />} />
        <MetricCard title="Accuracy" value={`${(stats.accuracy_rate * 100).toFixed(1)}%`} subtitle={`${stats.correct_count} correct · ${stats.incorrect_count} incorrect`} icon={<CheckCircle className="w-5 h-5" />} color="green" />
        <MetricCard title="Confidence" value={`${(stats.avg_confidence * 100).toFixed(1)}%`} icon={<TrendingUp className="w-5 h-5" />} />
        <MetricCard title="Quality" value={`${(stats.avg_final_score * 100).toFixed(1)}%`} icon={<BarChart3 className="w-5 h-5" />} color="yellow" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {/* Trend */}
        <div className="card p-5">
          <div className="flex items-center justify-between mb-5">
            <h3 className="text-[13px] font-semibold text-surface-400">Trend</h3>
            <span className="text-[10px] text-surface-700">30d</span>
          </div>
          {trends && trends.trends.length > 0 ? (
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trends.trends}>
                  <defs>
                    <linearGradient id="gt" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#fafafa" stopOpacity={0.08} />
                      <stop offset="100%" stopColor="#fafafa" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gc" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#10b981" stopOpacity={0.15} />
                      <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="date" tick={{ fill: '#404040', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: '#404040', fontSize: 10 }} axisLine={false} tickLine={false} width={25} />
                  <Tooltip contentStyle={tt} labelStyle={{ color: '#737373' }} />
                  <Area type="monotone" dataKey="total" stroke="#525252" fill="url(#gt)" strokeWidth={1.5} />
                  <Area type="monotone" dataKey="correct" stroke="#10b981" fill="url(#gc)" strokeWidth={1.5} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center text-surface-700 text-[12px]">No data</div>
          )}
        </div>

        {/* Issues */}
        <div className="card p-5">
          <h3 className="text-[13px] font-semibold text-surface-400 mb-5">Issues</h3>
          {Object.keys(stats.issue_distribution).length > 0 ? (
            <div className="space-y-3.5">
              {Object.entries(stats.issue_distribution).sort(([, a], [, b]) => b - a).map(([issue, count]) => {
                const total = Object.values(stats.issue_distribution).reduce((a, b) => a + b, 0);
                const pct = total > 0 ? (count / total) * 100 : 0;
                return (
                  <div key={issue}>
                    <div className="flex items-center justify-between text-[12px] mb-1.5">
                      <span className="text-surface-300 capitalize font-medium">{issue}</span>
                      <span className="text-surface-600 font-mono text-[11px]">{count}</span>
                    </div>
                    <div className="h-1 bg-[#1a1a1a] rounded-full overflow-hidden">
                      <div className="h-full bg-surface-500 rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center text-surface-700 text-[12px]">None</div>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="px-5 py-3.5 border-b border-[#1a1a1a]">
          <h3 className="text-[13px] font-semibold text-surface-400">Recent</h3>
        </div>
        {stats.recent_evaluations.length > 0 ? (
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#1a1a1a]">
                {['Prompt', 'Accuracy', 'Confidence', 'Severity', 'Score'].map(h => (
                  <th key={h} className="px-5 py-2.5 text-left text-[10px] font-semibold text-surface-600 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {stats.recent_evaluations.map((e) => (
                <tr key={e.id} className="border-b border-[#111] hover:bg-[#111] transition-colors">
                  <td className="px-5 py-3 text-[12px] text-surface-400 max-w-[250px] truncate">{e.prompt}</td>
                  <td className="px-5 py-3"><AccuracyBadge accuracy={e.accuracy} /></td>
                  <td className="px-5 py-3 text-[12px] text-surface-500 font-mono">{(e.confidence * 100).toFixed(0)}%</td>
                  <td className="px-5 py-3"><SeverityBadge severity={e.severity} /></td>
                  <td className="px-5 py-3 text-[12px] font-semibold text-surface-300">{e.final_score ? (e.final_score * 100).toFixed(0) + '%' : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="py-12 text-center text-surface-700 text-[12px]">No evaluations yet</div>
        )}
      </div>
    </div>
  );
}
