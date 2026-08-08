/**
 * components/SignalTable.tsx
 * Table of detected signals with modulation classification badges.
 */
import React from 'react';
import { DetectedSignal } from '../services/api';
import { Signal, Zap } from 'lucide-react';

interface SignalTableProps {
  signals: DetectedSignal[];
  loading?: boolean;
}

const MOD_COLORS: Record<string, string> = {
  AM:    'bg-sky-500/15 text-sky-400 border-sky-500/30',
  FM:    'bg-purple-500/15 text-purple-400 border-purple-500/30',
  USB:   'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  LSB:   'bg-teal-500/15 text-teal-400 border-teal-500/30',
  CW:    'bg-amber-500/15 text-amber-400 border-amber-500/30',
  BPSK:  'bg-pink-500/15 text-pink-400 border-pink-500/30',
  QPSK:  'bg-orange-500/15 text-orange-400 border-orange-500/30',
  '8PSK':'bg-red-500/15 text-red-400 border-red-500/30',
};

function ModBadge({ mod, confidence }: { mod?: string; confidence?: number }) {
  if (!mod) return <span className="text-slate-600 text-xs">—</span>;
  const cls = MOD_COLORS[mod] ?? 'bg-slate-500/15 text-slate-400 border-slate-500/30';
  return (
    <div className="flex items-center gap-2">
      <span className={`px-2 py-0.5 rounded-md text-xs font-mono font-semibold border ${cls}`}>
        {mod}
      </span>
      {confidence !== undefined && (
        <div className="flex items-center gap-1">
          <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-cyan-500 rounded-full"
              style={{ width: `${confidence * 100}%` }}
            />
          </div>
          <span className="text-xs text-slate-500 font-mono">{(confidence * 100).toFixed(0)}%</span>
        </div>
      )}
    </div>
  );
}

function SNRBar({ snr }: { snr: number }) {
  // SNR typically 0–40 dB; clamp to 0–40 for display
  const pct = Math.max(0, Math.min(100, (snr / 40) * 100));
  const color = snr > 20 ? 'bg-green-500' : snr > 10 ? 'bg-amber-500' : 'bg-red-500';
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-mono text-slate-300">{snr.toFixed(1)} dB</span>
    </div>
  );
}

export default function SignalTable({ signals, loading = false }: SignalTableProps) {
  return (
    <div className="bg-slate-900 rounded-xl border border-slate-700">
      {/* Header */}
      <div className="flex items-center gap-2 px-5 py-3 border-b border-slate-700">
        <Signal size={15} className="text-cyan-400" />
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Detected Signals
        </span>
        {signals.length > 0 && (
          <span className="ml-auto px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-400
                           text-xs font-mono border border-cyan-500/25">
            {signals.length}
          </span>
        )}
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-800">
              {['#', 'Freq (MHz)', 'BW (kHz)', 'Power (dBFS)', 'SNR', 'Modulation'].map(h => (
                <th
                  key={h}
                  className="px-4 py-2.5 text-left text-xs font-medium text-slate-500
                             uppercase tracking-wider whitespace-nowrap"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-slate-600 text-sm">
                  <div className="flex items-center justify-center gap-2">
                    <Zap size={14} className="animate-pulse text-cyan-500" />
                    Analysing…
                  </div>
                </td>
              </tr>
            )}
            {!loading && signals.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-slate-600 text-sm">
                  No signals detected. Start capture or lower threshold.
                </td>
              </tr>
            )}
            {!loading && signals.map((sig, idx) => (
              <tr
                key={idx}
                className="border-b border-slate-800/50 hover:bg-slate-800/40 transition-colors"
              >
                <td className="px-4 py-3 text-xs font-mono text-slate-600">{idx + 1}</td>
                <td className="px-4 py-3 font-mono text-cyan-300 text-xs">
                  {(sig.center_freq / 1e6).toFixed(4)}
                </td>
                <td className="px-4 py-3 font-mono text-slate-300 text-xs">
                  {(sig.bandwidth_hz / 1e3).toFixed(1)}
                </td>
                <td className="px-4 py-3 font-mono text-slate-300 text-xs">
                  {sig.power_db.toFixed(1)}
                </td>
                <td className="px-4 py-3">
                  <SNRBar snr={sig.snr_db} />
                </td>
                <td className="px-4 py-3">
                  <ModBadge mod={sig.modulation ?? undefined} confidence={sig.confidence ?? undefined} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
