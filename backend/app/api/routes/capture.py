"""
api/routes/capture.py — SDR capture endpoints.

POST /api/capture/start  — create a new capture session (metadata only)
GET  /api/capture/demo   — generate synthetic IQ samples
GET  /api/capture/sessions — list all sessions
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.config import settings
from app.models.capture import CaptureRequest, CaptureResponse, IQDataResponse
from app.models.analysis_result import SessionSummary
from app.models.signal import CaptureSession
from app.services.sdr_service import generate_demo_iq

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/start", response_model=CaptureResponse, summary="Start a new capture session")
def start_capture(request: CaptureRequest, db: Session = Depends(get_db)):
    """
    Create a new capture session record in the database.
    For demo mode, actual IQ data is not stored — call /demo to get samples.
    """
    session = CaptureSession(
        mode=request.mode,
        center_freq=request.center_freq,
        sample_rate=request.sample_rate,
        num_samples=request.num_samples,
        notes=request.notes,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    logger.info("New capture session #%d started (mode=%s)", session.id, session.mode)

    return CaptureResponse(
        session_id=session.id,
        mode=session.mode,
        center_freq=session.center_freq,
        sample_rate=session.sample_rate,
        num_samples=session.num_samples,
        created_at=session.created_at,
        message=f"Session #{session.id} created in {session.mode} mode.",
    )


@router.get("/demo", response_model=IQDataResponse, summary="Generate demo IQ samples")
def get_demo_iq(
    num_samples: int = None,
    sample_rate: float = None,
    center_freq: float = None,
    snr_db: float = 20.0,
    db: Session = Depends(get_db),
):
    """
    Generate synthetic IQ data with random modulation types.
    Creates and saves a capture session automatically.
    Returns I/Q arrays ready for FFT analysis.
    """
    n = num_samples or settings.DEMO_NUM_SAMPLES
    fs = sample_rate or settings.DEMO_SAMPLE_RATE
    fc = center_freq or settings.DEMO_CENTER_FREQ

    i_samples, q_samples, meta = generate_demo_iq(
        num_samples=n, sample_rate=fs, center_freq=fc, snr_db=snr_db
    )

    # Persist a session so we have a foreign key for analysis results
    session = CaptureSession(
        mode="demo",
        center_freq=fc,
        sample_rate=fs,
        num_samples=n,
        notes=f"Auto-generated demo: {len(meta)} signal(s)",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return IQDataResponse(
        session_id=session.id,
        sample_rate=fs,
        center_freq=fc,
        i_samples=i_samples,
        q_samples=q_samples,
        num_samples=n,
    )


@router.get("/sessions", response_model=list[SessionSummary], summary="List all capture sessions")
def list_sessions(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Return a paginated list of all capture sessions."""
    sessions = (
        db.query(CaptureSession)
        .order_by(CaptureSession.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return sessions


@router.get("/{session_id}", response_model=SessionSummary, summary="Get session by ID")
def get_session(session_id: int, db: Session = Depends(get_db)):
    """Retrieve a single capture session by ID."""
    session = db.query(CaptureSession).filter(CaptureSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
    return session
