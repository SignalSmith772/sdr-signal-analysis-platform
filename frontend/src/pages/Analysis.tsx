/**
 * pages/Analysis.tsx
 * Deep-dive analysis: run FFT with configurable parameters,
 * view spectrum + waterfall side-by-side, classify all signals.
 */
import React, { useState } from 'react';
import { BarChart2, Cpu, Play, ChevronDown } from 'lucide-react';
import SpectrumChart from '../components/SpectrumChart';
import WaterfallView from '../components/WaterfallView';
import SignalTable from '../components/SignalTable';
import {
  captureApi, analysisApi, classificationApi,
  FFTResponse, DetectionResponse, DetectedSignal
} from '../services/api';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const MOD_COLORS_PIE = ['#06b6d4','#a855f7','#22c55e','#f59e0b','#f43f5e','#3b82f6','#ec4899','#14b8a6'];

export default function Analysis() {
  const [fftSize, setFftSize] = useState(1024);
  const [snrDb, setSnrDb] = useState(20);
  const [numSamples, setNumSamples] = useState(2048);
  const [threshold, setThreshold] = useState(10);
  const [loading, setLoading] = useState(false);
  const [classifying, setClassifying] = useState(false);
  const [fftData, setFftData] = useState<FFTResponse | null>(null);
  const [detection, setDetection] = useState<DetectionResponse | null>(null);
  const [signals, setSignals] = useState<DetectedSignal[]>([]);
  const [modStats, setModStats] = useState<{ name: string; value: number }[]>([]);

  const runAnalysis = async () => {
    setLoading(true);
    setSignals([]);
    setModStats([]);
    try {
      // 1) Get demo IQ
      const iq = await captureApi.getDemo({ num_samples: numSamples, snr_db: snrDb });

      // 2) FFT
      const fft = await analysisApi.runFFT({
        i_samples: iq.i_samples,
        q_samples: iq.q_samples,
        sample_rate: iq.sample_rate,
        center_freq: iq.center_freq,
        fft_size: fftSize,
        session_id: iq.session_id,
      });
      setFftData(fft);

      // 3) Detect
      const det = await analysisApi.detect({
        frequencies: fft.frequencies,
        powers_db: fft.powers_db,
        noise_floor_db: fft.noise_floor_db,
        sample_rate: iq.sample_rate,
        center_freq: iq.center_freq,
        threshold_db: threshold,
      });
      setDetection(det);
      setSignals(det.signals);
    } catch (e: any) {
      alert('Analysis failed: ' + (e?.message || e));
    } finally {
      setLoading(false);
    }
  };

  const runClassification = async () => {
    if (!fftData || signals.length === 0) return;
    setClassifying(true);
    try {
      const classified = await Promise.all(
        signals.map(async sig => {
          const n = 256;
          const t = Array.from({ length: n }, (_, k) => k / 2_400_000);
          const freq = sig.center_freq;
          const i_s = t.map(ti => Math.cos(2 * Math.PI * freq * ti));
          const q_s = t.map(ti => Math.sin(2 * Math.PI * freq * ti));
          try {
            const cls = await classificationApi.classify({ i_samples: i_s, q_samples: q_s, sample_rate: 2_400_000 });
            return { ...sig, modulation: cls.modulation, confidence: cls.confidence };
          } catch { return sig; }
        })
      );
      setSignals(classified);

      // Build modulation stats for pie chart
      const counts: Record<string, number> = {};
      classified.forEach(s => {
        if (s.modulation) counts[s.modulation] = (counts[s.modulation] ?? 0) + 1;
      });
      setModStats(Object.entries(counts).map(([name, value]) => ({ name, value })));
    } finally {
      setClassifying(false);
    }
  };

  return (
    <div className="space-y-6 max-w-screen-2xl">
      <div>
        <h1 className="text-xl font-bold text-slate-100">Signal Analysis</h1>
        <p className="text-sm text-slate-500 mt-0.5">Configure FFT parameters and run deep analysis</p>
      </div>

      {/* Controls */}
      <div className="bg-slate-900 border border-slate-700 rounded-xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <BarChart2 size={15} className="text-cyan-400" />
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Analysis Parameters</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-5">
          {[
            { label: 'FFT Size', value: fftSize, setter: setFftSize, options: [256, 512, 1024, 2048, 4096] },
            { label: 'Samples',  value: numSamples, setter: setNumSamples, options: [512, 1024, 2048, 4096] },
            { label: 'SNR (dB)', value: snrDb, setter: setSnrDb, options: [5, 10, 15, 20, 30] },
            { label: 'Threshold (dB)', value: threshold, setter: setThreshold, options: [5, 10, 15, 20] },
          ].map(({ label, value, setter, options }) => (
            <div key={label}>
              <label className="block text-xs text-slate-400 mb-1">{label}</label>
              <div className="relative">
                <select
                  value={value}
                  onChange={e => setter(Number(e.target.value))}
                  className="w-full bg-slate-800 border border-slate-600 text-slate-200
                             text-sm rounded-lg px-3 py-2 appearance-none font-mono"
                >
                  {options.map(o => <option key={o} value={o}>{o}</option>)}
                </select>
                <ChevronDown size={12} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
              </div>
            </div>
          ))}
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            onClick={runAnalysis}
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-cyan-600
                       hover:bg-cyan-500 disabled:opacity-50 text-white text-sm font-semibold transition-colors"
          >
            <Play size={14} className={loading ? 'animate-pulse' : ''} />
            {loading ? 'Running…' : 'Run Analysis'}
          </button>
          <button
            onClick={runClassification}
            disabled={signals.length === 0 || classifying}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-purple-600
                       hover:bg-purple-500 disabled:opacity-40 text-white text-sm font-semibold transition-colors"
          >
            <Cpu size={14} className={classifying ? 'animate-spin' : ''} />
            {classifying ? 'Classifying…' : 'Classify Modulations'}
          </button>
        </div>
      </div>

      {/* Spectrum + Waterfall */}
      {fftData && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <SpectrumChart
            frequencies={fftData.frequencies}
            powersDb={fftData.powers_db}
            noiseFloorDb={fftData.noise_floor_db}
            peakFreq={fftData.peak_freq}
            height={280}
          />
          <WaterfallView
            powersDb={fftData.powers_db}
            noiseFloorDb={fftData.noise_floor_db}
            height={280}
          />
        </div>
      )}

      {/* Signals + Pie */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2">
          <SignalTable signals={signals} loading={classifying} />
        </div>

        {/* Modulation distribution pie */}
        <div className="bg-slate-900 border border-slate-700 rounded-xl p-5">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">
            Modulation Distribution
          </p>
          {modStats.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={modStats}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  strokeWidth={0}
                >
                  {modStats.map((_, idx) => (
                    <Cell key={idx} fill={MOD_COLORS_PIE[idx % MOD_COLORS_PIE.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
                  labelStyle={{ color: '#94a3b8' }}
                />
                <Legend
                  iconType="circle"
                  iconSize={8}
                  wrapperStyle={{ fontSize: 11, color: '#94a3b8' }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[220px] flex items-center justify-center text-slate-600 text-sm">
              Run classification to see distribution
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
