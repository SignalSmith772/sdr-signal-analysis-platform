"""
services/detection_service.py — Peak detection and band occupancy analysis.

Uses scipy's find_peaks on the FFT power spectrum to locate discrete
signals and measure their properties (centre frequency, bandwidth, SNR).
"""
import numpy as np
from scipy.signal import find_peaks
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def detect_signals(
    frequencies: List[float],
    powers_db: List[float],
    noise_floor_db: float,
    sample_rate: float,
    center_freq: float,
    threshold_db: float = 10.0,
) -> dict:
    """
    Detect signal peaks in a power spectrum.

    Parameters
    ----------
    frequencies   : Frequency axis in Hz (same length as powers_db)
    powers_db     : Power spectrum in dBFS
    noise_floor_db: Estimated noise floor in dBFS
    sample_rate   : Hz — used to compute bin width
    center_freq   : Hz — used for absolute frequency reporting
    threshold_db  : Minimum peak height above noise floor (dB)

    Returns
    -------
    dict with 'signals' list and 'band_occupancy_pct'
    """
    freqs = np.array(frequencies)
    powers = np.array(powers_db)
    n_bins = len(powers)

    # Absolute threshold for peak detection
    abs_threshold = noise_floor_db + threshold_db

    # find_peaks params:
    #   height   — must exceed abs_threshold
    #   distance — minimum spacing between peaks (avoid duplicate detection)
    #   prominence — ensures peaks stand above their local surroundings
    min_distance = max(1, n_bins // 64)   # at least 1 bin apart
    peak_indices, peak_props = find_peaks(
        powers,
        height=abs_threshold,
        distance=min_distance,
        prominence=5.0,   # dB prominence
    )

    signals: List[Dict] = []
    bin_width_hz = sample_rate / n_bins

    for idx in peak_indices:
        peak_pwr = float(powers[idx])
        peak_f = float(freqs[idx])
        snr = peak_pwr - noise_floor_db

        # Estimate 3-dB bandwidth by walking down from peak
        half_power = peak_pwr - 3.0
        left = idx
        right = idx
        while left > 0 and powers[left] > half_power:
            left -= 1
        while right < n_bins - 1 and powers[right] > half_power:
            right += 1
        bw = float((right - left) * bin_width_hz)

        signals.append(
            {
                "center_freq": peak_f,
                "bandwidth_hz": max(bw, bin_width_hz),
                "power_db": peak_pwr,
                "snr_db": round(snr, 2),
                "modulation": None,
                "confidence": None,
            }
        )

    # Band occupancy — fraction of bins above threshold
    occupied = float(np.mean(powers > abs_threshold)) * 100.0

    logger.info(
        "Detection: found %d signals, band occupancy=%.1f%%", len(signals), occupied
    )

    return {
        "signals": signals,
        "band_occupancy_pct": round(occupied, 2),
        "total_detected": len(signals),
    }
