"""
models/signal.py — SQLAlchemy ORM models for the SDR platform.
Tables: capture_sessions, analysis_results, detected_signals.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, Float, String, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class CaptureSession(Base):
    """
    Represents one SDR capture session (real or demo).
    Stores metadata; raw samples are kept in memory / processed immediately.
    """
    __tablename__ = "capture_sessions"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    mode = Column(String(20), default="demo")          # "demo" | "live"
    center_freq = Column(Float, nullable=False)        # Hz
    sample_rate = Column(Float, nullable=False)        # Hz
    num_samples = Column(Integer, nullable=False)
    duration_ms = Column(Float, nullable=True)         # capture duration
    notes = Column(Text, nullable=True)

    # One session → many analysis results
    results = relationship("AnalysisResult", back_populates="session", cascade="all, delete-orphan")


class AnalysisResult(Base):
    """
    Stores FFT analysis + detected peaks for a capture session.
    """
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("capture_sessions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # FFT metadata
    fft_size = Column(Integer, nullable=False)
    peak_frequency = Column(Float, nullable=True)     # Hz of strongest peak
    peak_power_db = Column(Float, nullable=True)      # dBFS
    noise_floor_db = Column(Float, nullable=True)
    bandwidth_hz = Column(Float, nullable=True)       # occupied bandwidth

    # Stored as JSON arrays (lists of floats)
    frequencies_json = Column(JSON, nullable=True)    # freq axis
    powers_db_json = Column(JSON, nullable=True)      # power spectrum

    session = relationship("CaptureSession", back_populates="results")
    signals = relationship("DetectedSignal", back_populates="result", cascade="all, delete-orphan")


class DetectedSignal(Base):
    """
    Individual signal peak detected within an analysis result.
    """
    __tablename__ = "detected_signals"

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("analysis_results.id"), nullable=False)

    center_freq = Column(Float, nullable=False)       # Hz
    bandwidth_hz = Column(Float, nullable=False)
    power_db = Column(Float, nullable=False)
    snr_db = Column(Float, nullable=True)

    # ML classification output
    modulation = Column(String(20), nullable=True)    # e.g. "FM", "BPSK"
    confidence = Column(Float, nullable=True)         # 0.0 – 1.0

    result = relationship("AnalysisResult", back_populates="signals")
