/**
 * services/api.ts — Axios-based API client for the SDR backend.
 * All endpoints are typed and centralised here.
 */
import axios from 'axios';

// const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const BASE_URL = process.env.REACT_APP_API_URL || 'https://sdr-signal-analysis-platform-backend.onrender.com';

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30_000,
  headers: { 'Content-Type': 'application/json' },
});

// ── Types ─────────────────────────────────────────────────────────────────────

export interface IQDataResponse {
  session_id: number;
  sample_rate: number;
  center_freq: number;
  i_samples: number[];
  q_samples: number[];
  num_samples: number;
}

export interface FFTResponse {
  frequencies: number[];
  powers_db: number[];
  peak_freq: number;
  peak_power_db: number;
  noise_floor_db: number;
  bandwidth_hz: number;
  result_id?: number;
}

export interface DetectedSignal {
  center_freq: number;
  bandwidth_hz: number;
  power_db: number;
  snr_db: number;
  modulation?: string;
  confidence?: number;
}

export interface DetectionResponse {
  signals: DetectedSignal[];
  band_occupancy_pct: number;
  total_detected: number;
}

export interface ClassifyResponse {
  modulation: string;
  confidence: number;
  all_scores: Record<string, number>;
}

export interface SessionSummary {
  id: number;
  created_at: string;
  mode: string;
  center_freq_mhz: number;
  sample_rate_mhz: number;
  num_samples: number;
  num_analyses: number;
  notes?: string;
}

export interface CaptureStartResponse {
  session_id: number;
  mode: string;
  center_freq: number;
  sample_rate: number;
  num_samples: number;
  created_at: string;
  message: string;
}

// ── Capture endpoints ─────────────────────────────────────────────────────────

export const captureApi = {
  /** Generate synthetic demo IQ data */
  getDemo: (params?: {
    num_samples?: number;
    sample_rate?: number;
    center_freq?: number;
    snr_db?: number;
  }): Promise<IQDataResponse> =>
    api.get('/api/capture/demo', { params }).then(r => r.data),

  /** Start a new session */
  start: (body: {
    mode?: string;
    center_freq?: number;
    sample_rate?: number;
    num_samples?: number;
    notes?: string;
  }): Promise<CaptureStartResponse> =>
    api.post('/api/capture/start', body).then(r => r.data),

  /** List all sessions */
  listSessions: (): Promise<any[]> =>
    api.get('/api/capture/sessions').then(r => r.data),
};

// ── Analysis endpoints ────────────────────────────────────────────────────────

export const analysisApi = {
  /** Run FFT on IQ samples */
  runFFT: (body: {
    i_samples: number[];
    q_samples: number[];
    sample_rate: number;
    center_freq: number;
    fft_size?: number;
    session_id?: number;
  }): Promise<FFTResponse> =>
    api.post('/api/analysis/fft', body).then(r => r.data),

  /** Detect signal peaks from spectrum */
  detect: (body: {
    frequencies: number[];
    powers_db: number[];
    noise_floor_db: number;
    sample_rate: number;
    center_freq: number;
    threshold_db?: number;
  }): Promise<DetectionResponse> =>
    api.post('/api/analysis/detect', body).then(r => r.data),
};

// ── Classification endpoints ──────────────────────────────────────────────────

export const classificationApi = {
  classify: (body: {
    i_samples: number[];
    q_samples: number[];
    sample_rate: number;
  }): Promise<ClassifyResponse> =>
    api.post('/api/classification/classify', body).then(r => r.data),

  getLabels: (): Promise<{ labels: string[]; count: number }> =>
    api.get('/api/classification/labels').then(r => r.data),
};

// ── Reports endpoints ─────────────────────────────────────────────────────────

export const reportsApi = {
  listSessions: (): Promise<SessionSummary[]> =>
    api.get('/api/reports/sessions').then(r => r.data),

  getReport: (sessionId: number): Promise<any> =>
    api.get(`/api/reports/${sessionId}`).then(r => r.data),

  getCsvUrl: (sessionId: number): string =>
    `${BASE_URL}/api/reports/${sessionId}/csv`,
};
