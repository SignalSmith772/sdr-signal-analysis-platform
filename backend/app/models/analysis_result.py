"""
models/analysis_result.py — Pydantic schemas for analysis & classification endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ── FFT Analysis ─────────────────────────────────────────────────────────────

class FFTRequest(BaseModel):
    """Client sends raw IQ samples for FFT processing."""
    session_id: Optional[int] = None
    i_samples: List[float]
    q_samples: List[float]
    sample_rate: float = Field(default=2_400_000)
    center_freq: float = Field(default=100_000_000)
    fft_size: int = Field(default=1024, ge=64, le=8192)


class FFTResponse(BaseModel):
    frequencies: List[float]    # Hz (relative to center_freq)
    powers_db: List[float]      # dBFS power spectrum
    peak_freq: float            # Hz of dominant peak
    peak_power_db: float
    noise_floor_db: float
    bandwidth_hz: float
    result_id: Optional[int] = None


# ── Signal Detection ──────────────────────────────────────────────────────────

class DetectedSignalSchema(BaseModel):
    center_freq: float
    bandwidth_hz: float
    power_db: float
    snr_db: float
    modulation: Optional[str] = None
    confidence: Optional[float] = None


class DetectionRequest(BaseModel):
    frequencies: List[float]
    powers_db: List[float]
    noise_floor_db: float
    sample_rate: float = 2_400_000
    center_freq: float = 100_000_000
    threshold_db: float = Field(default=10.0, description="dB above noise floor to count as signal")


class DetectionResponse(BaseModel):
    signals: List[DetectedSignalSchema]
    band_occupancy_pct: float   # % of band with signal present
    total_detected: int


# ── Classification ────────────────────────────────────────────────────────────

class ClassifyRequest(BaseModel):
    i_samples: List[float]
    q_samples: List[float]
    sample_rate: float = 2_400_000


class ClassifyResponse(BaseModel):
    modulation: str
    confidence: float
    all_scores: dict[str, float]   # label → probability


# ── Session list ──────────────────────────────────────────────────────────────

class SessionSummary(BaseModel):
    id: int
    created_at: datetime
    mode: str
    center_freq: float
    sample_rate: float
    num_samples: int
    notes: Optional[str]

    class Config:
        from_attributes = True
