"""
services/report_service.py — Session report generation.
Assembles JSON and CSV reports from the SQLite database.
"""
import io
import json
import csv
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models.signal import CaptureSession, AnalysisResult, DetectedSignal

logger = logging.getLogger(__name__)


def get_session_report(session_id: int, db: Session) -> Optional[dict]:
    """
    Build a full JSON report for a capture session.
    Returns None if the session does not exist.
    """
    session = db.query(CaptureSession).filter(CaptureSession.id == session_id).first()
    if session is None:
        return None

    results = []
    for result in session.results:
        signals = [
            {
                "center_freq_hz": s.center_freq,
                "bandwidth_hz": s.bandwidth_hz,
                "power_db": s.power_db,
                "snr_db": s.snr_db,
                "modulation": s.modulation,
                "confidence": s.confidence,
            }
            for s in result.signals
        ]
        results.append(
            {
                "result_id": result.id,
                "created_at": result.created_at.isoformat(),
                "fft_size": result.fft_size,
                "peak_frequency_hz": result.peak_frequency,
                "peak_power_db": result.peak_power_db,
                "noise_floor_db": result.noise_floor_db,
                "bandwidth_hz": result.bandwidth_hz,
                "detected_signals": signals,
            }
        )

    return {
        "report_generated_at": datetime.utcnow().isoformat(),
        "session": {
            "id": session.id,
            "mode": session.mode,
            "center_freq_hz": session.center_freq,
            "sample_rate_hz": session.sample_rate,
            "num_samples": session.num_samples,
            "created_at": session.created_at.isoformat(),
            "notes": session.notes,
        },
        "analyses": results,
        "summary": {
            "total_analyses": len(results),
            "total_signals_detected": sum(len(r["detected_signals"]) for r in results),
        },
    }


def get_session_csv(session_id: int, db: Session) -> Optional[str]:
    """
    Build a CSV report of detected signals for a session.
    Returns None if the session does not exist.
    """
    session = db.query(CaptureSession).filter(CaptureSession.id == session_id).first()
    if session is None:
        return None

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "session_id", "result_id", "center_freq_hz", "bandwidth_hz",
        "power_db", "snr_db", "modulation", "confidence",
    ])

    for result in session.results:
        for sig in result.signals:
            writer.writerow([
                session_id, result.id,
                sig.center_freq, sig.bandwidth_hz,
                sig.power_db, sig.snr_db,
                sig.modulation, sig.confidence,
            ])

    return output.getvalue()
