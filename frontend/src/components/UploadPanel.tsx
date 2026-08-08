/**
 * components/UploadPanel.tsx
 * Allows uploading a binary IQ file (.bin / .iq / .raw / .cs8 / .cf32)
 * or falling back to demo data generation.
 */
import React, { useRef, useState, useCallback } from 'react';
import { Upload, FileType, AlertCircle, CheckCircle2 } from 'lucide-react';
import { captureApi, analysisApi, IQDataResponse, FFTResponse } from '../services/api';

interface UploadPanelProps {
  onData: (iq: IQDataResponse, fft: FFTResponse) => void;
}

type Status = 'idle' | 'loading' | 'success' | 'error';

const ACCEPTED = '.bin,.iq,.raw,.cs8,.cf32';

export default function UploadPanel({ onData }: UploadPanelProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<Status>('idle');
  const [message, setMessage] = useState('');
  const [dragging, setDragging] = useState(false);

  // Parse raw binary float32 interleaved IQ file (most common format)
  const parseBinaryIQ = (buffer: ArrayBuffer): { i: number[]; q: number[] } => {
    const floats = new Float32Array(buffer);
    const i: number[] = [];
    const q: number[] = [];
    for (let n = 0; n < floats.length - 1; n += 2) {
      i.push(floats[n]);
      q.push(floats[n + 1]);
    }
    return { i, q };
  };

  const processFile = useCallback(async (file: File) => {
    setStatus('loading');
    setMessage(`Reading ${file.name}…`);
    try {
      const buffer = await file.arrayBuffer();
      const { i, q } = parseBinaryIQ(buffer);
      // Truncate to first 4096 samples
      const i_s = i.slice(0, 4096);
      const q_s = q.slice(0, 4096);

      setMessage('Running FFT…');
      const fft = await analysisApi.runFFT({
        i_samples: i_s,
        q_samples: q_s,
        sample_rate: 2_400_000,
        center_freq: 100_000_000,
        fft_size: Math.min(1024, i_s.length),
      });

      const iqResp: IQDataResponse = {
        session_id: -1,
        sample_rate: 2_400_000,
        center_freq: 100_000_000,
        i_samples: i_s,
        q_samples: q_s,
        num_samples: i_s.length,
      };

      onData(iqResp, fft);
      setStatus('success');
      setMessage(`Loaded ${i_s.length} samples from ${file.name}`);
    } catch (err: any) {
      setStatus('error');
      setMessage(err?.message || 'Failed to process file.');
    }
  }, [onData]);

  const handleDemo = async () => {
    setStatus('loading');
    setMessage('Generating demo IQ data…');
    try {
      const iq = await captureApi.getDemo({ num_samples: 2048 });
      const fft = await analysisApi.runFFT({
        i_samples: iq.i_samples,
        q_samples: iq.q_samples,
        sample_rate: iq.sample_rate,
        center_freq: iq.center_freq,
        fft_size: 1024,
        session_id: iq.session_id,
      });
      onData(iq, fft);
      setStatus('success');
      setMessage(`Demo: ${iq.num_samples} synthetic samples generated`);
    } catch (err: any) {
      setStatus('error');
      setMessage(err?.message || 'Failed to connect to backend. Is the server running?');
    }
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  }, [processFile]);

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-700 p-6">
      <h3 className="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wider">
        Load IQ Data
      </h3>

      {/* Drop zone */}
      <div
        onDragOver={e => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => fileRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
          dragging
            ? 'border-cyan-400 bg-cyan-500/5'
            : 'border-slate-600 hover:border-slate-500 hover:bg-slate-800/40'
        }`}
      >
        <Upload size={28} className={`mx-auto mb-3 ${dragging ? 'text-cyan-400' : 'text-slate-500'}`} />
        <p className="text-sm text-slate-400 font-medium">
          Drop IQ file here or click to browse
        </p>
        <p className="text-xs text-slate-600 mt-1">
          Supports: .bin .iq .raw .cs8 .cf32 (interleaved float32)
        </p>
        <input
          ref={fileRef}
          type="file"
          accept={ACCEPTED}
          className="hidden"
          onChange={e => { if (e.target.files?.[0]) processFile(e.target.files[0]); }}
        />
      </div>

      {/* Divider */}
      <div className="flex items-center gap-3 my-4">
        <div className="flex-1 border-t border-slate-700" />
        <span className="text-xs text-slate-600">or</span>
        <div className="flex-1 border-t border-slate-700" />
      </div>

      {/* Demo button */}
      <button
        onClick={handleDemo}
        disabled={status === 'loading'}
        className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg
                   bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed
                   text-white font-semibold text-sm transition-colors"
      >
        <FileType size={16} />
        {status === 'loading' ? 'Loading…' : 'Generate Demo Data'}
      </button>

      {/* Status */}
      {status !== 'idle' && (
        <div className={`mt-4 flex items-start gap-2 p-3 rounded-lg text-xs ${
          status === 'success' ? 'bg-green-500/10 border border-green-500/25 text-green-400' :
          status === 'error'   ? 'bg-red-500/10 border border-red-500/25 text-red-400' :
                                 'bg-slate-800 border border-slate-700 text-slate-400'
        }`}>
          {status === 'success' && <CheckCircle2 size={14} className="shrink-0 mt-0.5" />}
          {status === 'error'   && <AlertCircle  size={14} className="shrink-0 mt-0.5" />}
          <span>{message}</span>
        </div>
      )}
    </div>
  );
}
