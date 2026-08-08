"""
api/routes/reports.py — Session report export endpoints.

GET /api/reports/sessions          — list sessions summary
GET /api/reports/{session_id}      — full JSON report
GET /api/reports/{session_id}/csv  — CSV export of detected signals
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.signal import CaptureSession
from app.services.report_service import get_session_report, get_session_csv

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/sessions", summary="List all sessions for reporting")
def list_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Return a summary list of all capture sessions."""
    sessions = (
        db.query(CaptureSession)
        .order_by(CaptureSession.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": s.id,
            "created_at": s.created_at.isoformat(),
            "mode": s.mode,
            "center_freq_mhz": round(s.center_freq / 1e6, 3),
            "sample_rate_mhz": round(s.sample_rate / 1e6, 3),
            "num_samples": s.num_samples,
            "num_analyses": len(s.results),
            "notes": s.notes,
        }
        for s in sessions
    ]


@router.get("/{session_id}", summary="Export full session report as JSON")
def export_json(session_id: int, db: Session = Depends(get_db)):
    """
    Generate a complete JSON report for a session, including all
    FFT results and detected signals with classifications.
    """
    report = get_session_report(session_id, db)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
    return report


@router.get("/{session_id}/csv", summary="Export detected signals as CSV")
def export_csv(session_id: int, db: Session = Depends(get_db)):
    """Download a CSV file of all detected signals in a session."""
    csv_data = get_session_csv(session_id, db)
    if csv_data is None:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=session_{session_id}_signals.csv"
        },
    )
