/**
 * components/SpectrumChart.tsx
 * Real-time FFT spectrum display using Recharts.
 * Shows power (dBFS) vs frequency (MHz) with noise floor line.
 */
import React, { useMemo } from 'react';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, ReferenceLine, Legend,
} from 'recharts';

interface SpectrumChartProps {
  frequencies: number[];   // Hz
  powersDb: number[];      // dBFS
  noiseFloorDb?: number;
  peakFreq?: number;       // Hz
  height?: number;
}

// Custom tooltip
function SpectrumTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  return (
    <div className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-xs font-mono shadow-xl">
      <p className="text-cyan-400">{Number(d?.freq).toFixed(4)} MHz</p>
      <p className="text-emerald-400">{Number(d?.power).toFixed(1)} dBFS</p>
    </div>
  );
}

export default function SpectrumChart({
  frequencies,
  powersDb,
  noiseFloorDb,
  peakFreq,
  height = 260,
}: SpectrumChartProps) {
  // Downsample to max 512 points for rendering performance
  const data = useMemo(() => {
    if (!frequencies.length) return [];
    const step = Math.max(1, Math.floor(frequencies.length / 512));
    const points = [];
    for (let i = 0; i < frequencies.length; i += step) {
      points.push({
        freq: frequencies[i] / 1e6,          // convert to MHz
        power: Math.max(powersDb[i], -120),   // clamp floor
      });
    }
    return points;
  }, [frequencies, powersDb]);

  const yMin = noiseFloorDb !== undefined ? noiseFloorDb - 10 : -100;
  const yMax = 0;

  if (!data.length) {
    return (
      <div
        style={{ height }}
        className="flex items-center justify-center bg-slate-900 rounded-xl border border-slate-700"
      >
        <p className="text-slate-500 text-sm">No spectrum data — start capture to view</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-700 p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Power Spectrum
        </span>
        {noiseFloorDb !== undefined && (
          <span className="text-xs font-mono text-slate-500">
            Noise floor: {noiseFloorDb.toFixed(1)} dBFS
          </span>
        )}
      </div>
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="spectrumGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#06b6d4" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis
            dataKey="freq"
            tickFormatter={v => `${v.toFixed(1)}`}
            tick={{ fontSize: 10, fill: '#64748b', fontFamily: 'JetBrains Mono' }}
            label={{ value: 'MHz', position: 'insideRight', offset: -4, fill: '#475569', fontSize: 10 }}
            stroke="#334155"
          />
          <YAxis
            domain={[yMin, yMax]}
            tickFormatter={v => `${v}`}
            tick={{ fontSize: 10, fill: '#64748b', fontFamily: 'JetBrains Mono' }}
            label={{ value: 'dBFS', angle: -90, position: 'insideLeft', fill: '#475569', fontSize: 10 }}
            stroke="#334155"
            width={42}
          />
          <Tooltip content={<SpectrumTooltip />} />
          {/* Noise floor reference line */}
          {noiseFloorDb !== undefined && (
            <ReferenceLine
              y={noiseFloorDb}
              stroke="#f59e0b"
              strokeDasharray="4 4"
              strokeWidth={1}
              label={{ value: 'Noise', fill: '#f59e0b', fontSize: 9, position: 'right' }}
            />
          )}
          {/* Peak frequency marker */}
          {peakFreq !== undefined && (
            <ReferenceLine
              x={peakFreq / 1e6}
              stroke="#a855f7"
              strokeDasharray="4 4"
              strokeWidth={1}
              label={{ value: 'Peak', fill: '#a855f7', fontSize: 9, position: 'top' }}
            />
          )}
          <Area
            type="monotone"
            dataKey="power"
            stroke="#06b6d4"
            strokeWidth={1.5}
            fill="url(#spectrumGrad)"
            dot={false}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
