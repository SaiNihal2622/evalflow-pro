import { Inbox, AlertCircle } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description?: string;
}

export default function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <Inbox className="w-8 h-8 text-surface-700 mb-4" />
      <h3 className="text-sm font-semibold text-surface-400">{title}</h3>
      {description && <p className="text-[12px] text-surface-600 mt-1">{description}</p>}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <AlertCircle className="w-8 h-8 text-red-500/50 mb-4" />
      <h3 className="text-sm font-semibold text-surface-400">Something went wrong</h3>
      <p className="text-[12px] text-surface-600 mt-1">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="btn-secondary mt-4 text-[12px]">Retry</button>
      )}
    </div>
  );
}
