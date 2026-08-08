/**
 * pages/Dashboard.tsx
 * Main landing page: live spectrum, waterfall, signal table, and metric cards.
 * Polls the backend automatically in demo mode.
 */
import React, { useState } from 'react';
import { Play, Square, RefreshCw, Settings } from 'lucide-react';
import MetricsCards from '../components/MetricsCards';
import SpectrumChart from '../components/SpectrumChart';
import WaterfallView from '../components/WaterfallView';
import SignalTable from '../components/SignalTable';
import { useLiveSpectrum } from '../hooks/useLiveSpectrum';
import { classificationApi } from '../services/api';
import { DetectedSignal } from '../services/api';

export default function Dashboard() {
  const [classifiedSignals, setClassifiedSignals] = useState<DetectedSignal[]>([]);
  const [classifying, setClassifying] = useState(false);
  const [interval, setIntervalMs] = useState(2000);

  const {
    fftData, detection, isRunning, error, frameCount,
    start, stop, toggle,
  } = useLiveSpectrum({
    intervalMs: interval,
    autoStart: false,
    numSamples: 2048,
    fftSize: 512,
  });

  // After detection, run ML classification on each signal's frequency window
  const handleClassify = async () => {
    if (!fftData || !detection) return;
    setClassifying(true);
    try {
      const results = await Promise.all(
        detection.signals.slice(0, 6).map(async sig => {
          // Extract a narrow band of the spectrum around each detected signal
          const freqs = fftData.frequencies;
          const powers = fftData.powers_db;
          const bw = sig.bandwidth_hz;
          const idxs = freqs
            .map((f, i) => ({ f, i }))
            .filter(({ f }) => Math.abs(f - sig.center_freq) < bw);
          // Use fake-but-consistent IQ for demo (real app would extract from session)
          const n = 256;
          const t = Array.from({ length: n }, (_, k) => k / 2_400_000);
          const offset = sig.center_freq - (fftData.frequencies[0] ?? 100e6);
          const i_s = t.map(ti => Math.cos(2 * Math.PI * offset * ti));
          const q_s = t.map(ti => Math.sin(2 * Math.PI * offset * ti));

          try {
            const cls = await classificationApi.classify({
              i_samples: i_s,
              q_samples: q_s,
              sample_rate: 2_400_000,
            });
            return { ...sig, modulation: cls.modulation, confidence: cls.confidence };
          } catch {
            return sig;
          }
        })
      );
      setClassifiedSignals(results);
    } finally {
      setClassifying(false);
    }
  };

  const displaySignals = classifiedSignals.length > 0
    ? classifiedSignals
    : (detection?.signals ?? []);

  return (
    <div className="space-y-6 max-w-screen-2xl">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100">Live Dashboard</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Real-time spectrum analysis · Demo mode · Frame #{frameCount}
          </p>
        </div>
        <div className="sm:ml-auto flex items-center gap-2 flex-wrap">
          {/* Update rate picker */}
          <select
            value={interval}
            onChange={e => setIntervalMs(Number(e.target.value))}
            disabled={isRunning}
            className="bg-slate-800 border border-slate-700 text-slate-300 text-xs
                       rounded-lg px-3 py-2 disabled:opacity-50"
          >
            <option value={500}>500 ms</option>
            <option value={1000}>1 s</option>
            <option value={2000}>2 s</option>
            <option value={5000}>5 s</option>
          </select>

          <button
            onClick={handleClassify}
            disabled={!fftData || classifying}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-600
                       hover:bg-purple-500 disabled:opacity-40 disabled:cursor-not-allowed
                       text-white text-sm font-medium transition-colors"
          >
            <RefreshCw size={14} className={classifying ? 'animate-spin' : ''} />
            {classifying ? 'Classifying…' : 'Run ML'}
          </button>

          <button
            onClick={toggle}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-white
                        text-sm font-semibold transition-colors ${
              isRunning
                ? 'bg-red-600 hover:bg-red-500'
                : 'bg-cyan-600 hover:bg-cyan-500'
            }`}
          >
            {isRunning ? <><Square size={14} /> Stop</> : <><Play size={14} /> Start</>}
          </button>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/25 text-red-400 rounded-xl
                        px-4 py-3 text-sm flex items-center gap-2">
          <span className="font-semibold">Error:</span> {error}
          <span className="text-red-500/60 text-xs ml-2">
            Make sure the backend is running on port 8000.
          </span>
        </div>
      )}

      {/* Metric cards */}
      <MetricsCards
        peakFreqMHz={fftData ? fftData.peak_freq / 1e6 : undefined}
        peakPowerDb={fftData?.peak_power_db}
        noiseFloorDb={fftData?.noise_floor_db}
        bandwidthKHz={fftData ? fftData.bandwidth_hz / 1e3 : undefined}
        signalCount={detection?.total_detected}
        bandOccupancy={detection?.band_occupancy_pct}
        isLive={isRunning}
      />

      {/* Spectrum + Waterfall */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <SpectrumChart
          frequencies={fftData?.frequencies ?? []}
          powersDb={fftData?.powers_db ?? []}
          noiseFloorDb={fftData?.noise_floor_db}
          peakFreq={fftData?.peak_freq}
          height={260}
        />
        <WaterfallView
          powersDb={fftData?.powers_db ?? []}
          noiseFloorDb={fftData?.noise_floor_db ?? -80}
          height={260}
        />
      </div>

      {/* Signal table */}
      <SignalTable
        signals={displaySignals}
        loading={classifying}
      />
    </div>
  );
}
