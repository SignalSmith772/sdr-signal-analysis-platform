"""
ml/preprocessing/feature_extraction.py
Stand-alone feature extraction script for the ML pipeline.
Can be used outside of the FastAPI context for batch processing.
"""
import numpy as np
from scipy.stats import kurtosis, skew
from scipy.signal import hilbert
from typing import List


FEATURE_NAMES = [
    "spectral_entropy",
    "spectral_flatness",
    "peak_to_mean_ratio",
    "kurtosis_i",
    "kurtosis_q",
    "skewness_i",
    "skewness_q",
    "iq_imbalance",
    "am_std",
    "fm_std",
    "pm_std",
    "envelope_mean",
]


def extract_features(i_samples: List[float], q_samples: List[float]) -> np.ndarray:
    """
    Extract a 12-dimensional feature vector from IQ samples.
    Matches the features used during training in train_model.py.
    """
    i = np.asarray(i_samples, dtype=np.float64)
    q = np.asarray(q_samples, dtype=np.float64)
    iq = i + 1j * q

    # Instantaneous signals
    envelope = np.abs(iq)
    phase = np.angle(iq)
    inst_freq = np.diff(np.unwrap(phase))

    # Spectral
    fft_mag = np.abs(np.fft.fft(iq))
    fft_norm = fft_mag / (np.sum(fft_mag) + 1e-12)

    spectral_entropy = float(-np.sum(fft_norm * np.log2(fft_norm + 1e-12)))
    log_mean = np.mean(np.log(fft_norm + 1e-12))
    spectral_flatness = float(np.exp(log_mean) / (np.mean(fft_norm + 1e-12)))
    power = fft_norm ** 2
    peak_to_mean = float(np.max(power) / (np.mean(power) + 1e-12))

    return np.array([
        spectral_entropy,
        spectral_flatness,
        peak_to_mean,
        float(kurtosis(i)),
        float(kurtosis(q)),
        float(skew(i)),
        float(skew(q)),
        float(np.std(envelope) / (np.mean(envelope) + 1e-12)),
        float(np.std(envelope)),
        float(np.std(inst_freq)),
        float(np.std(np.diff(phase))),
        float(np.mean(envelope)),
    ], dtype=np.float64)


def batch_extract(iq_blocks: List[tuple]) -> np.ndarray:
    """
    Extract features from multiple IQ blocks.

    Parameters
    ----------
    iq_blocks : list of (i_samples, q_samples) tuples

    Returns
    -------
    np.ndarray of shape (N, 12)
    """
    return np.vstack([extract_features(i, q) for i, q in iq_blocks])
