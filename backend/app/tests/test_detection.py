"""
tests/test_detection.py — Unit tests for the signal detection service.
Run: pytest app/tests/test_detection.py -v
"""
import numpy as np
import pytest
from app.services.detection_service import detect_signals


def _flat_spectrum(n: int = 512, noise_db: float = -80.0) -> tuple[list, list]:
    """Flat noise spectrum — no peaks."""
    freqs = np.linspace(-1_200_000, 1_200_000, n).tolist()
    powers = (np.ones(n) * noise_db).tolist()
    return freqs, powers


def _spectrum_with_peak(peak_idx: int = 256, peak_db: float = -40.0,
                        noise_db: float = -80.0, n: int = 512):
    freqs = np.linspace(-1_200_000, 1_200_000, n)
    powers = np.ones(n) * noise_db
    powers[peak_idx - 2 : peak_idx + 3] = peak_db   # 5-bin wide peak
    return freqs.tolist(), powers.tolist()


class TestDetectSignals:
    def test_no_signals_in_flat_spectrum(self):
        freqs, powers = _flat_spectrum()
        result = detect_signals(freqs, powers, noise_floor_db=-80.0,
                                sample_rate=2_400_000, center_freq=100e6)
        assert result["total_detected"] == 0
        assert result["signals"] == []

    def test_single_peak_detected(self):
        freqs, powers = _spectrum_with_peak(peak_idx=256, peak_db=-40.0, noise_db=-80.0)
        result = detect_signals(freqs, powers, noise_floor_db=-80.0,
                                sample_rate=2_400_000, center_freq=100e6,
                                threshold_db=10.0)
        assert result["total_detected"] == 1

    def test_detected_signal_has_required_fields(self):
        freqs, powers = _spectrum_with_peak()
        result = detect_signals(freqs, powers, noise_floor_db=-80.0,
                                sample_rate=2_400_000, center_freq=100e6)
        if result["signals"]:
            sig = result["signals"][0]
            assert "center_freq" in sig
            assert "bandwidth_hz" in sig
            assert "power_db" in sig
            assert "snr_db" in sig

    def test_snr_is_positive_for_real_signal(self):
        freqs, powers = _spectrum_with_peak(peak_db=-40.0, noise_db=-80.0)
        result = detect_signals(freqs, powers, noise_floor_db=-80.0,
                                sample_rate=2_400_000, center_freq=100e6)
        if result["signals"]:
            assert result["signals"][0]["snr_db"] > 0

    def test_band_occupancy_between_0_and_100(self):
        freqs, powers = _spectrum_with_peak()
        result = detect_signals(freqs, powers, noise_floor_db=-80.0,
                                sample_rate=2_400_000, center_freq=100e6)
        assert 0.0 <= result["band_occupancy_pct"] <= 100.0

    def test_no_signals_below_threshold(self):
        """A 5 dB peak shouldn't be detected with a 10 dB threshold."""
        freqs = np.linspace(-1_200_000, 1_200_000, 512)
        powers = np.ones(512) * -80.0
        powers[255:260] = -75.0   # only 5 dB above noise
        result = detect_signals(
            freqs.tolist(), powers.tolist(), noise_floor_db=-80.0,
            sample_rate=2_400_000, center_freq=100e6, threshold_db=10.0
        )
        assert result["total_detected"] == 0
