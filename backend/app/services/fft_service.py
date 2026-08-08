"""
services/fft_service.py — FFT-based spectrum analysis.

Converts raw IQ samples into a calibrated power spectrum (dBFS),
computes the noise floor via median estimation, and measures
the occupied bandwidth.
"""
import numpy as np
from scipy.signal import get_window
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def compute_fft(
    i_samples: list[float],
    q_samples: list[float],
    sample_rate: float,
    center_freq: float,
    fft_size: int = 1024,
    window: str = "hann",
) -> dict:
    """
    Run FFT on complex IQ samples and return spectrum data.

    Parameters
    ----------
    i_samples   : In-phase (real) samples
    q_samples   : Quadrature (imaginary) samples
    sample_rate : Sampling rate in Hz
    center_freq : Receiver center frequency in Hz
    fft_size    : Number of FFT bins (will be clipped to len(samples))
    window      : Window function name (hann, blackman, flat_top, …)

    Returns
    -------
    dict with keys: frequencies, powers_db, peak_freq, peak_power_db,
                    noise_floor_db, bandwidth_hz
    """
    # Build complex array
    iq = np.array(i_samples, dtype=np.float64) + 1j * np.array(q_samples, dtype=np.float64)
    n = len(iq)

    # Use the smaller of fft_size and available samples
    fft_n = min(fft_size, n)

    # Apply window to reduce spectral leakage
    win = get_window(window, fft_n)
    win_power_correction = np.sum(win ** 2) / fft_n  # for accurate power

    # Compute FFT of windowed signal
    spectrum = np.fft.fftshift(np.fft.fft(iq[:fft_n] * win, n=fft_n))

    # Convert to power in dBFS (normalised to 0 dB = full scale)
    power = (np.abs(spectrum) ** 2) / (fft_n ** 2 * win_power_correction)
    power_db = 10 * np.log10(power + 1e-12)  # add epsilon to avoid log(0)

    # Frequency axis (relative to center_freq)
    freqs_rel = np.fft.fftshift(np.fft.fftfreq(fft_n, d=1.0 / sample_rate))
    freqs_abs = (center_freq + freqs_rel).tolist()

    # ── Metrics ──────────────────────────────────────────────────────────────

    # Noise floor: median of lower 80% of bins (robust to signal peaks)
    sorted_power = np.sort(power_db)
    noise_floor_db = float(np.median(sorted_power[: int(0.8 * len(sorted_power))]))

    # Peak
    peak_idx = int(np.argmax(power_db))
    peak_power_db = float(power_db[peak_idx])
    peak_freq = float(freqs_abs[peak_idx])

    # Occupied bandwidth: bins > noise_floor + 3 dB
    threshold = noise_floor_db + 3.0
    occupied_bins = np.sum(power_db > threshold)
    bin_width = sample_rate / fft_n
    bandwidth_hz = float(occupied_bins * bin_width)

    logger.debug(
        "FFT done: peak=%.1f dBFS @ %.3f MHz, noise=%.1f dBFS, BW=%.0f Hz",
        peak_power_db, peak_freq / 1e6, noise_floor_db, bandwidth_hz,
    )

    return {
        "frequencies": freqs_abs,
        "powers_db": power_db.tolist(),
        "peak_freq": peak_freq,
        "peak_power_db": peak_power_db,
        "noise_floor_db": noise_floor_db,
        "bandwidth_hz": bandwidth_hz,
    }


def build_waterfall_row(
    i_samples: list[float],
    q_samples: list[float],
    sample_rate: float,
    fft_size: int = 512,
) -> list[float]:
    """
    Return a single row of power values (dBFS) for waterfall display.
    Optimised for repeated calls — no frequency axis returned.
    """
    iq = np.array(i_samples, dtype=np.float64) + 1j * np.array(q_samples, dtype=np.float64)
    n = min(fft_size, len(iq))
    win = get_window("hann", n)
    spectrum = np.fft.fftshift(np.fft.fft(iq[:n] * win, n=n))
    power = (np.abs(spectrum) ** 2) / (n ** 2)
    return (10 * np.log10(power + 1e-12)).tolist()
