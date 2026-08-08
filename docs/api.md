# API Reference

Base URL: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

---

## Capture

### `GET /api/capture/demo`
Generate synthetic IQ data (no hardware needed).

**Query params:**
| Param | Type | Default | Description |
|---|---|---|---|
| num_samples | int | 4096 | IQ sample count |
| sample_rate | float | 2400000 | Hz |
| center_freq | float | 100000000 | Hz |
| snr_db | float | 20.0 | Signal-to-noise ratio |

**Response:**
```json
{
  "session_id": 1,
  "sample_rate": 2400000,
  "center_freq": 100000000,
  "i_samples": [0.12, -0.34, ...],
  "q_samples": [0.56, 0.78, ...],
  "num_samples": 4096
}
```

---

### `POST /api/capture/start`
Create a new capture session.

**Body:**
```json
{
  "mode": "demo",
  "center_freq": 100000000,
  "sample_rate": 2400000,
  "num_samples": 4096,
  "notes": "optional note"
}
```

---

### `GET /api/capture/sessions`
List all capture sessions (paginated).

---

## Analysis

### `POST /api/analysis/fft`
Run FFT on IQ samples.

**Body:**
```json
{
  "i_samples": [...],
  "q_samples": [...],
  "sample_rate": 2400000,
  "center_freq": 100000000,
  "fft_size": 1024,
  "session_id": 1
}
```

**Response:**
```json
{
  "frequencies": [...],
  "powers_db": [...],
  "peak_freq": 100050000,
  "peak_power_db": -32.5,
  "noise_floor_db": -80.1,
  "bandwidth_hz": 145000,
  "result_id": 3
}
```

---

### `POST /api/analysis/detect`
Detect signal peaks from a power spectrum.

**Body:**
```json
{
  "frequencies": [...],
  "powers_db": [...],
  "noise_floor_db": -80.1,
  "sample_rate": 2400000,
  "center_freq": 100000000,
  "threshold_db": 10.0
}
```

**Response:**
```json
{
  "signals": [
    {
      "center_freq": 100050000,
      "bandwidth_hz": 120000,
      "power_db": -40.2,
      "snr_db": 22.1,
      "modulation": null,
      "confidence": null
    }
  ],
  "band_occupancy_pct": 18.5,
  "total_detected": 1
}
```

---

## Classification

### `POST /api/classification/classify`
Classify the modulation type of IQ samples.

**Body:**
```json
{
  "i_samples": [...],
  "q_samples": [...],
  "sample_rate": 2400000
}
```

**Response:**
```json
{
  "modulation": "FM",
  "confidence": 0.94,
  "all_scores": {
    "AM": 0.02, "FM": 0.94, "USB": 0.01,
    "LSB": 0.01, "CW": 0.0, "BPSK": 0.01,
    "QPSK": 0.01, "8PSK": 0.0
  }
}
```

---

### `GET /api/classification/labels`
List all supported modulation types.

---

## Reports

### `GET /api/reports/sessions`
List all sessions with summary statistics.

### `GET /api/reports/{session_id}`
Full JSON report for a session.

### `GET /api/reports/{session_id}/csv`
Download detected signals as CSV file.
