export default function LoadingSpinner({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-24">
      <div className="w-5 h-5 border-2 border-surface-800 border-t-surface-400 rounded-full animate-spin mb-4" />
      <p className="text-[13px] text-surface-600">{message}</p>
    </div>
  );
}
