/**
 * pages/Reports.tsx
 * Session history, JSON report viewer, CSV export.
 */
import React, { useState, useEffect } from 'react';
import { FileText, Download, RefreshCw, ChevronRight, X } from 'lucide-react';
import { reportsApi, SessionSummary } from '../services/api';

function SessionRow({
  session,
  onView,
}: {
  session: SessionSummary;
  onView: (id: number) => void;
}) {
  return (
    <tr className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
      <td className="px-4 py-3 font-mono text-cyan-400 text-xs">#{session.id}</td>
      <td className="px-4 py-3 text-xs text-slate-400 whitespace-nowrap">
        {new Date(session.created_at).toLocaleString()}
      </td>
      <td className="px-4 py-3">
        <span className={`px-2 py-0.5 rounded text-xs font-mono border ${
          session.mode === 'demo'
            ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/25'
            : 'bg-green-500/10 text-green-400 border-green-500/25'
        }`}>
          {session.mode}
        </span>
      </td>
      <td className="px-4 py-3 font-mono text-xs text-slate-300">
        {Number(session.center_freq_mhz).toFixed(3)} MHz
      </td>
      <td className="px-4 py-3 font-mono text-xs text-slate-300">
        {Number(session.sample_rate_mhz).toFixed(2)} MSPS
      </td>
      <td className="px-4 py-3 font-mono text-xs text-slate-300">{session.num_analyses}</td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => onView(session.id)}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-700
                       hover:bg-slate-600 text-slate-300 text-xs transition-colors"
          >
            <ChevronRight size={12} /> View
          </button>
          <a
            href={reportsApi.getCsvUrl(session.id)}
            download={`session_${session.id}.csv`}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-700
                       hover:bg-slate-600 text-slate-300 text-xs transition-colors"
          >
            <Download size={12} /> CSV
          </a>
        </div>
      </td>
    </tr>
  );
}

function JSONModal({ sessionId, onClose }: { sessionId: number; onClose: () => void }) {
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    reportsApi.getReport(sessionId)
      .then(setReport)
      .catch(() => setReport({ error: 'Failed to load report' }))
      .finally(() => setLoading(false));
  }, [sessionId]);

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700 shrink-0">
          <div className="flex items-center gap-2">
            <FileText size={16} className="text-cyan-400" />
            <span className="font-semibold text-slate-200">Session #{sessionId} Report</span>
          </div>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-300 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* JSON content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="text-center text-slate-500 py-12">Loading report…</div>
          ) : (
            <pre className="text-xs text-slate-300 font-mono whitespace-pre-wrap break-words
                            bg-slate-950 rounded-xl p-4 border border-slate-800">
              {JSON.stringify(report, null, 2)}
            </pre>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-700 flex gap-3 shrink-0">
          <a
            href={reportsApi.getCsvUrl(sessionId)}
            download={`session_${sessionId}.csv`}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-600
                       hover:bg-cyan-500 text-white text-sm font-medium transition-colors"
          >
            <Download size={14} /> Download CSV
          </a>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600
                       text-slate-300 text-sm transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Reports() {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [viewId, setViewId] = useState<number | null>(null);

  const loadSessions = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await reportsApi.listSessions();
      setSessions(data);
    } catch (e: any) {
      setError('Could not load sessions. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadSessions(); }, []);

  return (
    <div className="space-y-6 max-w-screen-xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100">Reports</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Session history · JSON export · CSV download
          </p>
        </div>
        <button
          onClick={loadSessions}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800
                     hover:bg-slate-700 text-slate-300 text-sm transition-colors"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/25 text-red-400 rounded-xl px-4 py-3 text-sm">
          {error}
        </div>
      )}

      {/* Stats bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Total Sessions', value: sessions.length },
          { label: 'Demo Sessions',  value: sessions.filter(s => s.mode === 'demo').length },
          { label: 'Live Sessions',  value: sessions.filter(s => s.mode === 'live').length },
          { label: 'Total Analyses', value: sessions.reduce((acc, s) => acc + s.num_analyses, 0) },
        ].map(({ label, value }) => (
          <div key={label} className="bg-slate-900 border border-slate-700 rounded-xl p-4">
            <p className="text-xs text-slate-500 uppercase tracking-wider">{label}</p>
            <p className="text-2xl font-bold text-slate-100 mt-1 font-mono">{value}</p>
          </div>
        ))}
      </div>

      {/* Table */}
      <div className="bg-slate-900 border border-slate-700 rounded-xl overflow-hidden">
        <div className="px-5 py-3 border-b border-slate-700 flex items-center gap-2">
          <FileText size={14} className="text-cyan-400" />
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Capture Sessions
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800">
                {['ID', 'Created At', 'Mode', 'Center Freq', 'Sample Rate', 'Analyses', 'Actions'].map(h => (
                  <th key={h} className="px-4 py-2.5 text-left text-xs font-medium text-slate-500
                                         uppercase tracking-wider whitespace-nowrap">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td colSpan={7} className="px-4 py-10 text-center text-slate-600 text-sm">
                    Loading sessions…
                  </td>
                </tr>
              )}
              {!loading && sessions.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-4 py-10 text-center text-slate-600 text-sm">
                    No sessions yet. Go to Dashboard and start a capture!
                  </td>
                </tr>
              )}
              {!loading && sessions.map(s => (
                <SessionRow key={s.id} session={s} onView={setViewId} />
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Report modal */}
      {viewId !== null && (
        <JSONModal sessionId={viewId} onClose={() => setViewId(null)} />
      )}
    </div>
  );
}
