/**
 * pages/Capture.tsx
 * Manual capture controls and IQ file upload with instant preview.
 */
import React, { useState } from 'react';
import { Radio, Sliders } from 'lucide-react';
import UploadPanel from '../components/UploadPanel';
import SpectrumChart from '../components/SpectrumChart';
import SignalTable from '../components/SignalTable';
import { IQDataResponse, FFTResponse, analysisApi, DetectionResponse } from '../services/api';

export default function Capture() {
  const [iqData, setIqData] = useState<IQDataResponse | null>(null);
  const [fftData, setFftData] = useState<FFTResponse | null>(null);
  const [detection, setDetection] = useState<DetectionResponse | null>(null);
  const [detecting, setDetecting] = useState(false);

  const handleData = async (iq: IQDataResponse, fft: FFTResponse) => {
    setIqData(iq);
    setFftData(fft);
    setDetection(null);

    // Auto-detect signals
    setDetecting(true);
    try {
      const det = await analysisApi.detect({
        frequencies: fft.frequencies,
        powers_db: fft.powers_db,
        noise_floor_db: fft.noise_floor_db,
        sample_rate: iq.sample_rate,
        center_freq: iq.center_freq,
      });
      setDetection(det);
    } catch (e) {
      console.error('Detection failed', e);
    } finally {
      setDetecting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-screen-xl">
      <div>
        <h1 className="text-xl font-bold text-slate-100">Signal Capture</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Upload a binary IQ file or generate synthetic demo data
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: controls */}
        <div className="space-y-4">
          <UploadPanel onData={handleData} />

          {/* Session metadata panel */}
          {iqData && (
            <div className="bg-slate-900 border border-slate-700 rounded-xl p-4 space-y-3">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                <Sliders size={13} />
                Session Info
              </div>
              {[
                ['Session ID', `#${iqData.session_id}`],
                ['Center Freq', `${(iqData.center_freq / 1e6).toFixed(3)} MHz`],
                ['Sample Rate', `${(iqData.sample_rate / 1e6).toFixed(2)} MSPS`],
                ['Samples', iqData.num_samples.toLocaleString()],
                ['Signals Found', detection ? String(detection.total_detected) : '…'],
                ['Band Occ.', detection ? `${detection.band_occupancy_pct.toFixed(1)}%` : '…'],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between text-xs">
                  <span className="text-slate-500">{k}</span>
                  <span className="text-slate-200 font-mono">{v}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: spectrum */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-900 border border-slate-700 rounded-xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <Radio size={15} className="text-cyan-400" />
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Captured Spectrum Preview
              </span>
            </div>
            <SpectrumChart
              frequencies={fftData?.frequencies ?? []}
              powersDb={fftData?.powers_db ?? []}
              noiseFloorDb={fftData?.noise_floor_db}
              peakFreq={fftData?.peak_freq}
              height={280}
            />
          </div>

          <SignalTable
            signals={detection?.signals ?? []}
            loading={detecting}
          />
        </div>
      </div>
    </div>
  );
}
