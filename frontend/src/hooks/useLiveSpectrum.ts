/**
 * hooks/useLiveSpectrum.ts
 *
 * Custom hook that polls the backend every `intervalMs` ms to generate
 * fresh demo IQ data, run FFT, and detect signals — simulating a live
 * SDR feed without any real hardware.
 */
/* eslint-disable react-hooks/exhaustive-deps */
import { useState, useEffect, useRef, useCallback } from 'react';
import { captureApi, analysisApi, FFTResponse, DetectionResponse, IQDataResponse } from '../services/api';

interface LiveSpectrumState {
  iqData: IQDataResponse | null;
  fftData: FFTResponse | null;
  detection: DetectionResponse | null;
  isRunning: boolean;
  error: string | null;
  frameCount: number;
}

interface UseLiveSpectrumOptions {
  intervalMs?: number;
  autoStart?: boolean;
  numSamples?: number;
  sampleRate?: number;
  centerFreq?: number;
  snrDb?: number;
  fftSize?: number;
}

export function useLiveSpectrum(options: UseLiveSpectrumOptions = {}) {
  const {
    intervalMs = 1500,
    autoStart = false,
    numSamples = 1024,
    sampleRate = 2_400_000,
    centerFreq = 100_000_000,
    snrDb = 20,
    fftSize = 512,
  } = options;

  const [state, setState] = useState<LiveSpectrumState>({
    iqData: null,
    fftData: null,
    detection: null,
    isRunning: false,
    error: null,
    frameCount: 0,
  });

  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const runningRef = useRef(false);

  const fetchFrame = useCallback(async () => {
    if (!runningRef.current) return;
    try {
      // 1) Get demo IQ data
      const iq = await captureApi.getDemo({
        num_samples: numSamples,
        sample_rate: sampleRate,
        center_freq: centerFreq,
        snr_db: snrDb,
      });

      // 2) Run FFT
      const fft = await analysisApi.runFFT({
        i_samples: iq.i_samples,
        q_samples: iq.q_samples,
        sample_rate: sampleRate,
        center_freq: centerFreq,
        fft_size: fftSize,
      });

      // 3) Detect signals
      const det = await analysisApi.detect({
        frequencies: fft.frequencies,
        powers_db: fft.powers_db,
        noise_floor_db: fft.noise_floor_db,
        sample_rate: sampleRate,
        center_freq: centerFreq,
      });

      setState(prev => ({
        ...prev,
        iqData: iq,
        fftData: fft,
        detection: det,
        error: null,
        frameCount: prev.frameCount + 1,
      }));
    } catch (err: any) {
      setState(prev => ({
        ...prev,
        error: err?.message || 'Failed to fetch spectrum data',
      }));
    }
  }, [numSamples, sampleRate, centerFreq, snrDb, fftSize]);

  const start = useCallback(() => {
    if (runningRef.current) return;
    runningRef.current = true;
    setState(prev => ({ ...prev, isRunning: true, error: null }));
    fetchFrame(); // immediate first frame
    timerRef.current = setInterval(fetchFrame, intervalMs);
  }, [fetchFrame, intervalMs]);

  const stop = useCallback(() => {
    runningRef.current = false;
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setState(prev => ({ ...prev, isRunning: false }));
  }, []);

  const toggle = useCallback(() => {
    if (runningRef.current) stop();
    else start();
  }, [start, stop]);

  useEffect(() => {
    if (autoStart) start();
    return () => stop();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return { ...state, start, stop, toggle };
}
