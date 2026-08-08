"""
api/routes/analysis.py — FFT analysis and signal detection endpoints.

POST /api/analysis/fft      — run FFT on IQ samples
POST /api/analysis/detect   — detect signal peaks from spectrum
GET  /api/analysis/waterfall — get a waterfall row
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.config import settings
from app.models.analysis_result import (
    FFTRequest, FFTResponse,
    DetectionRequest, DetectionResponse,
)
from app.models.signal import AnalysisResult, DetectedSignal, CaptureSession
from app.services.fft_service import compute_fft, build_waterfall_row
from app.services.detection_service import detect_signals

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/fft", response_model=FFTResponse, summary="Run FFT spectrum analysis")
def run_fft(request: FFTRequest, db: Session = Depends(get_db)):
    """
    Compute FFT power spectrum from raw IQ samples.
    Optionally saves the result to the database if session_id is provided.
    """
    result = compute_fft(
        i_samples=request.i_samples,
        q_samples=request.q_samples,
        sample_rate=request.sample_rate,
        center_freq=request.center_freq,
        fft_size=request.fft_size,
    )

    result_id = None
    if request.session_id is not None:
        # Verify session exists
        session = db.query(CaptureSession).filter(
            CaptureSession.id == request.session_id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {request.session_id} not found.")

        # Save analysis result (store full spectrum as JSON)
        db_result = AnalysisResult(
            session_id=request.session_id,
            fft_size=request.fft_size,
            peak_frequency=result["peak_freq"],
            peak_power_db=result["peak_power_db"],
            noise_floor_db=result["noise_floor_db"],
            bandwidth_hz=result["bandwidth_hz"],
            frequencies_json=result["frequencies"],
            powers_db_json=result["powers_db"],
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        result_id = db_result.id
        logger.info("Saved FFT result #%d for session #%d", result_id, request.session_id)

    return FFTResponse(
        frequencies=result["frequencies"],
        powers_db=result["powers_db"],
        peak_freq=result["peak_freq"],
        peak_power_db=result["peak_power_db"],
        noise_floor_db=result["noise_floor_db"],
        bandwidth_hz=result["bandwidth_hz"],
        result_id=result_id,
    )


@router.post("/detect", response_model=DetectionResponse, summary="Detect signal peaks")
def run_detection(request: DetectionRequest, db: Session = Depends(get_db)):
    """
    Detect discrete signals in a power spectrum.
    Returns a list of detected signals with centre freq, bandwidth, power, and SNR.
    """
    result = detect_signals(
        frequencies=request.frequencies,
        powers_db=request.powers_db,
        noise_floor_db=request.noise_floor_db,
        sample_rate=request.sample_rate,
        center_freq=request.center_freq,
        threshold_db=request.threshold_db,
    )
    return DetectionResponse(**result)


@router.post("/waterfall-row", summary="Get single waterfall row")
def get_waterfall_row(
    i_samples: list[float],
    q_samples: list[float],
    sample_rate: float = 2_400_000,
    fft_size: int = 512,
):
    """
    Compute a single row of waterfall data (power vs frequency).
    Call repeatedly to build scrolling waterfall history.
    """
    row = build_waterfall_row(i_samples, q_samples, sample_rate, fft_size)
    return {"powers_db": row, "fft_size": fft_size}


@router.get("/results/{session_id}", summary="Get all analysis results for a session")
def get_results(session_id: int, db: Session = Depends(get_db)):
    """Return all FFT analysis results stored for a given session."""
    results = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.session_id == session_id)
        .all()
    )
    if not results:
        raise HTTPException(status_code=404, detail="No results found for this session.")

    return [
        {
            "id": r.id,
            "session_id": r.session_id,
            "created_at": r.created_at.isoformat(),
            "fft_size": r.fft_size,
            "peak_frequency": r.peak_frequency,
            "peak_power_db": r.peak_power_db,
            "noise_floor_db": r.noise_floor_db,
            "bandwidth_hz": r.bandwidth_hz,
            "signal_count": len(r.signals),
        }
        for r in results
    ]
