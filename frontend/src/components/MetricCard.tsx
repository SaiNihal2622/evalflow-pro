import type { ReactNode } from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: ReactNode;
  color?: 'default' | 'green' | 'red' | 'yellow';
}

const dotColors = {
  default: 'bg-white',
  green: 'bg-emerald-400',
  red: 'bg-red-400',
  yellow: 'bg-amber-400',
};

export default function MetricCard({ title, value, subtitle, icon, color = 'default' }: MetricCardProps) {
  return (
    <div className="card p-5 animate-fade-in">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className={`w-1.5 h-1.5 rounded-full ${dotColors[color]}`} />
            <p className="text-[11px] text-surface-500 font-medium uppercase tracking-wider">{title}</p>
          </div>
          <p className="text-[28px] font-bold text-white tracking-tight leading-none">{value}</p>
          {subtitle && <p className="text-[11px] text-surface-600 mt-2">{subtitle}</p>}
        </div>
        <div className="text-surface-700">{icon}</div>
      </div>
    </div>
  );
}
