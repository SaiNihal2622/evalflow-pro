interface BadgeProps {
  label: string;
  variant?: 'default' | 'success' | 'danger' | 'warning' | 'info';
  size?: 'sm' | 'md';
}

const styles = {
  default: 'bg-[#171717] text-surface-400 border-[#1a1a1a]',
  success: 'bg-emerald-500/8 text-emerald-400 border-emerald-500/10',
  danger: 'bg-red-500/8 text-red-400 border-red-500/10',
  warning: 'bg-amber-500/8 text-amber-400 border-amber-500/10',
  info: 'bg-blue-500/8 text-blue-400 border-blue-500/10',
};

export default function Badge({ label, variant = 'default', size = 'sm' }: BadgeProps) {
  return (
    <span className={`inline-flex items-center border rounded-md font-medium capitalize ${styles[variant]} ${
      size === 'sm' ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-0.5 text-[11px]'
    }`}>
      {label}
    </span>
  );
}

export function AccuracyBadge({ accuracy }: { accuracy: string }) {
  const variant = accuracy === 'correct' ? 'success' : accuracy === 'incorrect' ? 'danger' : 'default';
  return <Badge label={accuracy} variant={variant} />;
}

export function SeverityBadge({ severity }: { severity: string }) {
  const variant = severity === 'low' ? 'success' : severity === 'high' ? 'danger' : severity === 'medium' ? 'warning' : 'default';
  return <Badge label={severity} variant={variant} />;
}
