import {
  BarChart, Bar, PieChart, Pie, Cell, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import LoadingSpinner from '../components/LoadingSpinner';
import { ErrorState } from '../components/EmptyState';
import EmptyState from '../components/EmptyState';
import { useStats, useTrends, useIssueDistribution } from '../hooks/useApi';

const COLORS = ['#fafafa', '#a3a3a3', '#525252', '#737373', '#d4d4d4', '#404040'];
const ACC_COLORS = ['#10b981', '#ef4444', '#404040'];
const SEV: Record<string, string> = { low: '#10b981', medium: '#f59e0b', high: '#ef4444' };
const tt = { backgroundColor: '#111', border: '1px solid #1a1a1a', borderRadius: '8px', fontSize: '11px' };

export default function Analytics() {
  const { data: stats, loading: sl, error: se, refetch } = useStats();
  const { data: trends, loading: tl } = useTrends(30);
  const { data: issues, loading: il } = useIssueDistribution();

  if (sl || tl || il) return <LoadingSpinner message="Loading analytics..." />;
  if (se) return <ErrorState message={se} onRetry={refetch} />;
  if (!stats || stats.total_evaluations === 0) return (
    <div className="space-y-6">
      <div><h1 className="text-[22px] font-bold text-white">Analytics</h1><p className="text-surface-600 text-[13px] mt-1">Evaluation patterns and trends</p></div>
      <EmptyState title="No data" description="Run evaluations first." />
    </div>
  );

  const accData = [
    { name: 'Correct', value: stats.correct_count },
    { name: 'Incorrect', value: stats.incorrect_count },
    { name: 'Other', value: Math.max(0, stats.total_evaluations - stats.correct_count - stats.incorrect_count) },
  ].filter(d => d.value > 0);
  const sevData = Object.entries(stats.severity_distribution || {}).map(([name, value]) => ({ name, value }));
  const issueData = (issues?.issues || []).map(i => ({ name: i.issue, count: i.count }));

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-[22px] font-bold text-white">Analytics</h1>
        <p className="text-surface-600 text-[13px] mt-1">Evaluation patterns and trends</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card p-5">
          <h3 className="text-[13px] font-semibold text-surface-400 mb-4">Accuracy</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={accData} cx="50%" cy="50%" innerRadius={50} outerRadius={75} paddingAngle={2} dataKey="value" stroke="none">
                  {accData.map((_, i) => <Cell key={i} fill={ACC_COLORS[i % ACC_COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={tt} />
                <Legend formatter={(v) => <span style={{ color: '#737373', fontSize: '11px' }}>{v}</span>} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card p-5">
          <h3 className="text-[13px] font-semibold text-surface-400 mb-4">Severity</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={sevData} cx="50%" cy="50%" innerRadius={50} outerRadius={75} paddingAngle={2} dataKey="value" stroke="none">
                  {sevData.map((e) => <Cell key={e.name} fill={SEV[e.name] || '#404040'} />)}
                </Pie>
                <Tooltip contentStyle={tt} />
                <Legend formatter={(v) => <span style={{ color: '#737373', fontSize: '11px', textTransform: 'capitalize' }}>{v}</span>} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {issueData.length > 0 && (
        <div className="card p-5">
          <h3 className="text-[13px] font-semibold text-surface-400 mb-4">Issue Frequency</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={issueData} layout="vertical" margin={{ left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
                <XAxis type="number" tick={{ fill: '#404040', fontSize: 10 }} axisLine={false} />
                <YAxis type="category" dataKey="name" tick={{ fill: '#737373', fontSize: 11 }} axisLine={false} width={90} />
                <Tooltip contentStyle={tt} />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {issueData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {trends && trends.trends.length > 0 && (
        <div className="card p-5">
          <h3 className="text-[13px] font-semibold text-surface-400 mb-4">Trends (30d)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trends.trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
                <XAxis dataKey="date" tick={{ fill: '#404040', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#404040', fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tt} />
                <Legend formatter={(v) => <span style={{ color: '#737373', fontSize: '11px', textTransform: 'capitalize' }}>{v}</span>} />
                <Line type="monotone" dataKey="total" stroke="#fafafa" strokeWidth={1.5} dot={false} />
                <Line type="monotone" dataKey="correct" stroke="#10b981" strokeWidth={1.5} dot={false} />
                <Line type="monotone" dataKey="incorrect" stroke="#ef4444" strokeWidth={1.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {trends && trends.trends.length > 0 && (
        <div className="card p-5">
          <h3 className="text-[13px] font-semibold text-surface-400 mb-4">Confidence</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trends.trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
                <XAxis dataKey="date" tick={{ fill: '#404040', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis domain={[0, 1]} tick={{ fill: '#404040', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                <Tooltip contentStyle={tt} />
                <Line type="monotone" dataKey="avg_confidence" stroke="#f59e0b" strokeWidth={1.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
