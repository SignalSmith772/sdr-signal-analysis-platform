"""
services/ml_service.py — ML-based modulation classification.

Loads the pre-trained Random Forest model and extracts features from
raw IQ samples to predict the modulation type.

Feature set (12 features):
  Spectral: spectral_entropy, spectral_flatness, peak_to_mean_ratio
  Statistical: kurt_i, kurt_q, skew_i, skew_q, iq_imbalance
  Instantaneous: am_std, fm_std, pm_std, envelope_mean
"""
import os
import logging
import numpy as np
from scipy.stats import kurtosis, skew
import joblib
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Label list must match training order in train_model.py
MODULATION_LABELS = ["AM", "FM", "USB", "LSB", "CW", "BPSK", "QPSK", "8PSK"]

# Cached model — loaded once on first call
_model = None


def _get_model(model_path: str):
    """Lazy-load the trained model (cached in module-level variable)."""
    global _model
    if _model is None:
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"ML model not found at {model_path}. "
                "Run `python backend/scripts/train_model.py` first."
            )
        _model = joblib.load(model_path)
        logger.info("✅ Loaded ML model from %s", model_path)
    return _model


def extract_features(i_samples: list[float], q_samples: list[float]) -> np.ndarray:
    """
    Extract a 12-dimensional feature vector from IQ samples.
    Must match the feature extraction used during training.
    """
    i = np.array(i_samples, dtype=np.float64)
    q = np.array(q_samples, dtype=np.float64)
    iq = i + 1j * q

    # ── Instantaneous signals ─────────────────────────────────────────────────
    envelope = np.abs(iq)
    phase = np.angle(iq)
    inst_freq = np.diff(np.unwrap(phase))  # approximate instantaneous frequency

    # ── Spectral features (FFT magnitude) ────────────────────────────────────
    fft_mag = np.abs(np.fft.fft(iq))
    fft_mag /= (np.sum(fft_mag) + 1e-12)   # normalise to probability distribution

    # Spectral entropy (information-theoretic measure of spectral "peakiness")
    spectral_entropy = float(-np.sum(fft_mag * np.log2(fft_mag + 1e-12)))

    # Spectral flatness (geometric / arithmetic mean ratio)
    log_mean = np.mean(np.log(fft_mag + 1e-12))
    arithmetic_mean = np.mean(fft_mag + 1e-12)
    spectral_flatness = float(np.exp(log_mean) / arithmetic_mean)

    # Peak-to-mean power ratio
    power = fft_mag ** 2
    peak_to_mean = float(np.max(power) / (np.mean(power) + 1e-12))

    # ── Statistical features ─────────────────────────────────────────────────
    kurt_i = float(kurtosis(i))
    kurt_q = float(kurtosis(q))
    skew_i = float(skew(i))
    skew_q = float(skew(q))

    # IQ imbalance (amplitude difference between I and Q channels)
    iq_imbalance = float(np.std(envelope) / (np.mean(envelope) + 1e-12))

    # ── Instantaneous AM/FM/PM variance ──────────────────────────────────────
    am_std = float(np.std(envelope))
    fm_std = float(np.std(inst_freq))
    pm_std = float(np.std(np.diff(phase)))
    envelope_mean = float(np.mean(envelope))

    return np.array([
        spectral_entropy, spectral_flatness, peak_to_mean,
        kurt_i, kurt_q, skew_i, skew_q, iq_imbalance,
        am_std, fm_std, pm_std, envelope_mean,
    ], dtype=np.float64)


def classify_modulation(
    i_samples: list[float],
    q_samples: list[float],
    model_path: str,
) -> Dict:
    """
    Classify the modulation type of IQ samples.

    Returns
    -------
    dict with 'modulation', 'confidence', 'all_scores'
    """
    model = _get_model(model_path)
    features = extract_features(i_samples, q_samples).reshape(1, -1)

    predicted_label = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]

    # Map probabilities to label names
    all_scores = {label: round(float(prob), 4) for label, prob in zip(model.classes_, probabilities)}
    confidence = float(max(probabilities))

    logger.debug("Classification: %s (%.1f%%)", predicted_label, confidence * 100)

    return {
        "modulation": str(predicted_label),
        "confidence": round(confidence, 4),
        "all_scores": all_scores,
    }
