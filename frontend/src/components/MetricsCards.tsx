/**
 * components/MetricsCards.tsx
 * Summary metric cards shown at the top of the dashboard.
 */
import React from 'react';
import { Radio, Activity, Zap, TrendingUp } from 'lucide-react';

interface MetricsCardsProps {
  peakFreqMHz?: number;
  peakPowerDb?: number;
  noiseFloorDb?: number;
  bandwidthKHz?: number;
  signalCount?: number;
  bandOccupancy?: number;
  isLive?: boolean;
}

interface CardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  sub?: string;
  accent: string;
}

function MetricCard({ icon, label, value, sub, accent }: CardProps) {
  return (
    <div className={`bg-slate-800 border border-slate-700 rounded-xl p-4 flex items-start gap-4
                     hover:border-${accent}-500/50 transition-colors`}>
      <div className={`p-2.5 rounded-lg bg-${accent}-500/10 text-${accent}-400 shrink-0`}>
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-xs text-slate-400 uppercase tracking-wider font-medium">{label}</p>
        <p className="text-xl font-bold text-slate-100 mt-0.5 font-mono truncate">{value}</p>
        {sub && <p className="text-xs text-slate-500 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}

export default function MetricsCards({
  peakFreqMHz,
  peakPowerDb,
  noiseFloorDb,
  bandwidthKHz,
  signalCount,
  bandOccupancy,
  isLive = false,
}: MetricsCardsProps) {
  const fmt = (v?: number, decimals = 2, fallback = '—') =>
    v !== undefined && v !== null ? v.toFixed(decimals) : fallback;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
      {/* Live indicator card */}
      <div className="col-span-2 md:col-span-1 bg-slate-800 border border-slate-700 rounded-xl p-4 flex items-center gap-3">
        <span className={`w-3 h-3 rounded-full shrink-0 ${isLive ? 'bg-green-400 live-dot' : 'bg-slate-600'}`} />
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-wider font-medium">Status</p>
          <p className={`text-lg font-bold mt-0.5 ${isLive ? 'text-green-400' : 'text-slate-500'}`}>
            {isLive ? 'LIVE' : 'IDLE'}
          </p>
        </div>
      </div>

      <MetricCard
        icon={<Radio size={18} />}
        label="Peak Freq"
        value={peakFreqMHz !== undefined ? `${fmt(peakFreqMHz, 3)} MHz` : '—'}
        sub="dominant signal"
        accent="cyan"
      />
      <MetricCard
        icon={<TrendingUp size={18} />}
        label="Peak Power"
        value={peakPowerDb !== undefined ? `${fmt(peakPowerDb, 1)} dBFS` : '—'}
        sub={noiseFloorDb !== undefined ? `noise ${fmt(noiseFloorDb, 1)} dBFS` : undefined}
        accent="purple"
      />
      <MetricCard
        icon={<Activity size={18} />}
        label="Bandwidth"
        value={bandwidthKHz !== undefined ? `${fmt(bandwidthKHz, 1)} kHz` : '—'}
        sub="occupied"
        accent="amber"
      />
      <MetricCard
        icon={<Zap size={18} />}
        label="Signals"
        value={signalCount !== undefined ? String(signalCount) : '—'}
        sub={bandOccupancy !== undefined ? `${fmt(bandOccupancy, 1)}% band` : undefined}
        accent="green"
      />
    </div>
  );
}
