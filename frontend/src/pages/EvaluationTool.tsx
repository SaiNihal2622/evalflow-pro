import { useState } from 'react';
import { Send, RotateCcw } from 'lucide-react';
import { AccuracyBadge, SeverityBadge } from '../components/Badge';
import Badge from '../components/Badge';
import { useEvaluate } from '../hooks/useApi';

const TEMPLATES = [
  { label: 'Factual', prompt: 'What is the capital of France?', response: 'The capital of France is Paris. It is the largest city and serves as the political and cultural center.' },
  { label: 'Hallucination', prompt: 'Who invented the internet?', response: 'The internet was invented by Albert Einstein in 1972 at MIT, with approximately 89% of modern networks based on his design.' },
  { label: 'Incomplete', prompt: 'Explain the differences between TCP and UDP including use cases.', response: 'TCP is reliable.' },
  { label: 'Contradiction', prompt: 'Is coffee healthy?', response: 'Coffee is always good for health and increases lifespan. However, coffee is never good for health and decreases lifespan.' },
];

export default function EvaluationTool() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const { evaluate, result, loading, error } = useEvaluate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || !response.trim()) return;
    await evaluate(prompt, response).catch(() => {});
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-[22px] font-bold text-white">Evaluate</h1>
        <p className="text-surface-600 text-[13px] mt-1">Test AI responses with structured evaluation</p>
      </div>

      {/* Templates */}
      <div className="flex flex-wrap gap-2">
        {TEMPLATES.map((t) => (
          <button key={t.label} onClick={() => { setPrompt(t.prompt); setResponse(t.response); }} className="btn-secondary text-[12px] py-2">
            {t.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-5 gap-5">
        {/* Form */}
        <form onSubmit={handleSubmit} className="xl:col-span-3">
          <div className="card p-5 space-y-4">
            <div>
              <label className="block text-[12px] font-semibold text-surface-500 uppercase tracking-wider mb-2">Prompt</label>
              <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="The prompt given to the AI..." rows={3} className="input" style={{ resize: 'vertical' }} />
            </div>
            <div>
              <label className="block text-[12px] font-semibold text-surface-500 uppercase tracking-wider mb-2">Response</label>
              <textarea value={response} onChange={(e) => setResponse(e.target.value)} placeholder="The AI model's response..." rows={5} className="input" style={{ resize: 'vertical' }} />
            </div>
            <div className="flex gap-2 pt-1">
              <button type="submit" disabled={loading || !prompt.trim() || !response.trim()} className="btn-primary flex-1">
                {loading ? (
                  <><div className="w-3.5 h-3.5 border-2 border-black/20 border-t-black rounded-full animate-spin" /> Evaluating...</>
                ) : (
                  <><Send className="w-3.5 h-3.5" /> Evaluate</>
                )}
              </button>
              <button type="button" onClick={() => { setPrompt(''); setResponse(''); }} className="btn-secondary">
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </form>

        {/* Result */}
        <div className="xl:col-span-2">
          <div className="card h-full">
            <div className="px-5 py-3.5 border-b border-[#1a1a1a]">
              <h3 className="text-[13px] font-semibold text-surface-400">Result</h3>
            </div>
            <div className="p-5">
              {error && (
                <div className="p-3 rounded-lg bg-red-500/5 border border-red-500/10 text-red-400 text-[12px] mb-4">{error}</div>
              )}
              {result ? (
                <div className="space-y-5 animate-fade-in">
                  {/* Score */}
                  <div className="text-center py-4">
                    <div className="relative w-20 h-20 mx-auto">
                      <svg className="w-20 h-20 -rotate-90" viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="42" stroke="#1a1a1a" strokeWidth="5" fill="none" />
                        <circle cx="50" cy="50" r="42" stroke={result.final_score && result.final_score >= 0.7 ? '#10b981' : result.final_score && result.final_score >= 0.4 ? '#f59e0b' : '#ef4444'} strokeWidth="5" fill="none" strokeDasharray={`${(result.final_score || 0) * 264} 264`} strokeLinecap="round" />
                      </svg>
                      <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-xl font-bold text-white">{result.final_score ? (result.final_score * 100).toFixed(0) : '0'}</span>
                      </div>
                    </div>
                  </div>

                  {/* Details */}
                  <div className="space-y-2.5">
                    {[
                      { l: 'Accuracy', v: <AccuracyBadge accuracy={result.accuracy} /> },
                      { l: 'Severity', v: <SeverityBadge severity={result.severity} /> },
                      { l: 'Confidence', v: <span className="text-[12px] text-surface-300 font-mono">{(result.confidence * 100).toFixed(0)}%</span> },
                      { l: 'LLM Score', v: <span className="text-[12px] text-surface-300 font-mono">{result.llm_score != null ? (result.llm_score * 100).toFixed(0) + '%' : 'N/A'}</span> },
                      { l: 'Rule Score', v: <span className="text-[12px] text-surface-300 font-mono">{result.rule_score != null ? (result.rule_score * 100).toFixed(0) + '%' : 'N/A'}</span> },
                    ].map(({ l, v }) => (
                      <div key={l} className="flex items-center justify-between py-1.5 border-b border-[#111]">
                        <span className="text-[11px] text-surface-600 uppercase tracking-wider">{l}</span>
                        {v}
                      </div>
                    ))}
                  </div>

                  {result.issues.length > 0 && (
                    <div>
                      <p className="text-[11px] text-surface-600 uppercase tracking-wider mb-2">Issues</p>
                      <div className="flex flex-wrap gap-1">{result.issues.map((issue, i) => <Badge key={i} label={issue} variant="danger" size="md" />)}</div>
                    </div>
                  )}

                  {result.latency_ms != null && (
                    <p className="text-[10px] text-surface-700">{result.latency_ms}ms · #{result.id}</p>
                  )}
                </div>
              ) : (
                <div className="py-12 text-center">
                  <Send className="w-5 h-5 text-surface-800 mx-auto mb-3" />
                  <p className="text-surface-600 text-[12px]">Submit to see results</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
