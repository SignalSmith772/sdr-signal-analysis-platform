"""
api/routes/classification.py — ML modulation classification endpoint.

POST /api/classification/classify         — classify IQ samples
POST /api/classification/classify-signal  — classify + save to a detected signal
GET  /api/classification/labels           — list supported modulation types
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.config import settings
from app.models.analysis_result import ClassifyRequest, ClassifyResponse
from app.models.signal import DetectedSignal
from app.services.ml_service import classify_modulation, MODULATION_LABELS

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/classify", response_model=ClassifyResponse, summary="Classify modulation type")
def classify(request: ClassifyRequest):
    """
    Run ML classification on raw IQ samples.
    Returns the predicted modulation type and per-class probabilities.
    """
    try:
        result = classify_modulation(
            i_samples=request.i_samples,
            q_samples=request.q_samples,
            model_path=settings.ML_MODEL_PATH,
        )
        return ClassifyResponse(**result)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e) + " Run train_model.py to generate the model.",
        )


@router.post("/classify-signal/{signal_id}", response_model=ClassifyResponse,
             summary="Classify and update a detected signal")
def classify_and_save(
    signal_id: int,
    request: ClassifyRequest,
    db: Session = Depends(get_db),
):
    """
    Classify IQ samples and update the modulation/confidence on an existing
    DetectedSignal record in the database.
    """
    sig = db.query(DetectedSignal).filter(DetectedSignal.id == signal_id).first()
    if not sig:
        raise HTTPException(status_code=404, detail=f"Signal {signal_id} not found.")

    try:
        result = classify_modulation(
            i_samples=request.i_samples,
            q_samples=request.q_samples,
            model_path=settings.ML_MODEL_PATH,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    # Persist classification result
    sig.modulation = result["modulation"]
    sig.confidence = result["confidence"]
    db.commit()

    logger.info(
        "Signal #%d classified as %s (%.1f%%)",
        signal_id, result["modulation"], result["confidence"] * 100,
    )
    return ClassifyResponse(**result)


@router.get("/labels", summary="List supported modulation types")
def list_labels():
    """Return the list of modulation classes the model can predict."""
    return {"labels": MODULATION_LABELS, "count": len(MODULATION_LABELS)}
