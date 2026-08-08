"""
models/capture.py — Pydantic request/response schemas for capture endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CaptureRequest(BaseModel):
    """Body sent by the client to start a capture session."""
    mode: str = Field(default="demo", description="'demo' for synthetic data, 'live' for real SDR")
    center_freq: float = Field(default=100_000_000, description="Center frequency in Hz")
    sample_rate: float = Field(default=2_400_000, description="Sample rate in Hz")
    num_samples: int = Field(default=4096, ge=256, le=65536)
    notes: Optional[str] = None


class CaptureResponse(BaseModel):
    """Returned after a capture session is saved."""
    session_id: int
    mode: str
    center_freq: float
    sample_rate: float
    num_samples: int
    created_at: datetime
    message: str

    class Config:
        from_attributes = True


class IQDataResponse(BaseModel):
    """Raw IQ samples returned to the client for display."""
    session_id: int
    sample_rate: float
    center_freq: float
    # Interleaved real/imag or separate lists
    i_samples: list[float]
    q_samples: list[float]
    num_samples: int
