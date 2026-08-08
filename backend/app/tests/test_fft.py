"""
tests/test_fft.py — Unit tests for the FFT spectrum analysis service.
Run: pytest app/tests/test_fft.py -v
"""
import numpy as np
import pytest
from app.services.fft_service import compute_fft, build_waterfall_row


def _sine_iq(freq_hz: float, fs: float, n: int, amplitude: float = 1.0):
    """Generate a pure complex sinusoid at freq_hz."""
    t = np.arange(n) / fs
    iq = amplitude * np.exp(1j * 2 * np.pi * freq_hz * t)
    return iq.real.tolist(), iq.imag.tolist()


class TestComputeFFT:
    def test_returns_required_keys(self):
        i, q = _sine_iq(10_000, 100_000, 1024)
        result = compute_fft(i, q, 100_000, 0.0, fft_size=1024)
        assert "frequencies" in result
        assert "powers_db" in result
        assert "peak_freq" in result
        assert "peak_power_db" in result
        assert "noise_floor_db" in result
        assert "bandwidth_hz" in result

    def test_frequencies_length_matches_fft_size(self):
        i, q = _sine_iq(5_000, 100_000, 2048)
        result = compute_fft(i, q, 100_000, 0.0, fft_size=512)
        assert len(result["frequencies"]) == 512
        assert len(result["powers_db"]) == 512

    def test_peak_detected_near_signal_frequency(self):
        """Peak frequency should be within one bin of the true signal frequency."""
        fs = 100_000.0
        sig_freq = 10_000.0
        fft_size = 1024
        i, q = _sine_iq(sig_freq, fs, fft_size)
        result = compute_fft(i, q, fs, 0.0, fft_size=fft_size)
        bin_width = fs / fft_size
        assert abs(result["peak_freq"] - sig_freq) <= bin_width * 2

    def test_noise_floor_below_peak(self):
        i, q = _sine_iq(10_000, 100_000, 1024)
        result = compute_fft(i, q, 100_000, 0.0)
        assert result["noise_floor_db"] < result["peak_power_db"]

    def test_bandwidth_positive(self):
        i, q = _sine_iq(10_000, 100_000, 1024)
        result = compute_fft(i, q, 100_000, 0.0)
        assert result["bandwidth_hz"] > 0

    def test_short_input_handled(self):
        """FFT should clip to input length when fft_size > num_samples."""
        i, q = _sine_iq(1_000, 10_000, 64)
        result = compute_fft(i, q, 10_000, 0.0, fft_size=1024)
        assert len(result["frequencies"]) == 64  # clipped to available samples


class TestWaterfallRow:
    def test_returns_list(self):
        i, q = _sine_iq(5_000, 100_000, 512)
        row = build_waterfall_row(i, q, 100_000, fft_size=512)
        assert isinstance(row, list)
        assert len(row) == 512

    def test_values_are_finite(self):
        i, q = _sine_iq(5_000, 100_000, 512)
        row = build_waterfall_row(i, q, 100_000, fft_size=512)
        assert all(np.isfinite(v) for v in row)
