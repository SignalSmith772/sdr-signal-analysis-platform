"""
services/sdr_service.py — Synthetic IQ data generator (demo mode).

Produces realistic IQ samples for multiple modulation types so the entire
platform works without physical SDR hardware.  Each call to
`generate_demo_iq()` randomly places 1-4 signals in the band and mixes
them with AWGN.
"""
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

# Modulation types supported by the demo generator
DEMO_MODULATIONS = ["AM", "FM", "USB", "LSB", "CW", "BPSK", "QPSK", "8PSK"]


def _generate_am(t: np.ndarray, carrier: float, fs: float) -> np.ndarray:
    """Amplitude-modulated signal with a single audio tone."""
    audio_freq = 1000.0          # 1 kHz modulating tone
    modulation_index = 0.8
    audio = np.sin(2 * np.pi * audio_freq * t)
    carrier_wave = np.exp(1j * 2 * np.pi * carrier * t)
    return (1.0 + modulation_index * audio) * carrier_wave


def _generate_fm(t: np.ndarray, carrier: float, fs: float) -> np.ndarray:
    """Wideband FM with 75 kHz peak deviation."""
    audio_freq = 1000.0
    freq_dev = 75_000.0
    audio = np.sin(2 * np.pi * audio_freq * t)
    phase = 2 * np.pi * carrier * t + (freq_dev / audio_freq) * np.sin(2 * np.pi * audio_freq * t)
    return np.exp(1j * phase)


def _generate_ssb(t: np.ndarray, carrier: float, fs: float, upper: bool = True) -> np.ndarray:
    """Single-sideband (USB or LSB) voice signal."""
    audio_freq = 800.0
    audio = np.sin(2 * np.pi * audio_freq * t)
    sign = 1.0 if upper else -1.0
    # Hilbert approximation: analytic signal of audio
    from scipy.signal import hilbert
    analytic_audio = hilbert(audio)
    ssb = np.real(analytic_audio) * np.cos(2 * np.pi * carrier * t) \
        - sign * np.imag(analytic_audio) * np.sin(2 * np.pi * carrier * t)
    return ssb.astype(complex)


def _generate_cw(t: np.ndarray, carrier: float, fs: float) -> np.ndarray:
    """CW (Morse) — simple on/off keying at ~20 WPM."""
    dit = int(fs * 0.06)       # 60 ms dit
    pattern = np.zeros(len(t))
    pos = 0
    morse_pattern = [1, 0, 1, 0, 0, 1, 1, 1, 0, 1]  # SOS-like
    for bit in morse_pattern:
        end = min(pos + dit, len(t))
        if bit:
            pattern[pos:end] = 1.0
        pos = end
        if pos >= len(t):
            break
    return pattern * np.exp(1j * 2 * np.pi * carrier * t)


def _generate_bpsk(t: np.ndarray, carrier: float, fs: float) -> np.ndarray:
    """BPSK — random bits, symbol rate = fs/16."""
    symbol_rate = fs / 16
    num_bits = max(1, int(len(t) * symbol_rate / fs))
    bits = np.random.choice([-1, 1], size=num_bits)
    samples_per_sym = int(fs / symbol_rate)
    symbols = np.repeat(bits, samples_per_sym)[: len(t)]
    if len(symbols) < len(t):
        symbols = np.pad(symbols, (0, len(t) - len(symbols)), mode="edge")
    return symbols * np.exp(1j * 2 * np.pi * carrier * t)


def _generate_qpsk(t: np.ndarray, carrier: float, fs: float) -> np.ndarray:
    """QPSK — random dibits, symbol rate = fs/16."""
    symbol_rate = fs / 16
    num_sym = max(1, int(len(t) * symbol_rate / fs))
    angles = np.random.choice([0, np.pi / 2, np.pi, 3 * np.pi / 2], size=num_sym)
    samples_per_sym = int(fs / symbol_rate)
    phase_seq = np.repeat(angles, samples_per_sym)[: len(t)]
    if len(phase_seq) < len(t):
        phase_seq = np.pad(phase_seq, (0, len(t) - len(phase_seq)), mode="edge")
    return np.exp(1j * (2 * np.pi * carrier * t + phase_seq))


def _generate_8psk(t: np.ndarray, carrier: float, fs: float) -> np.ndarray:
    """8PSK — 8 equally spaced phase points."""
    symbol_rate = fs / 20
    num_sym = max(1, int(len(t) * symbol_rate / fs))
    angles = np.random.choice(
        [k * np.pi / 4 for k in range(8)], size=num_sym
    )
    samples_per_sym = int(fs / symbol_rate)
    phase_seq = np.repeat(angles, samples_per_sym)[: len(t)]
    if len(phase_seq) < len(t):
        phase_seq = np.pad(phase_seq, (0, len(t) - len(phase_seq)), mode="edge")
    return np.exp(1j * (2 * np.pi * carrier * t + phase_seq))


# Map modulation name → generator function
_GENERATORS = {
    "AM": _generate_am,
    "FM": _generate_fm,
    "USB": lambda t, c, fs: _generate_ssb(t, c, fs, upper=True),
    "LSB": lambda t, c, fs: _generate_ssb(t, c, fs, upper=False),
    "CW": _generate_cw,
    "BPSK": _generate_bpsk,
    "QPSK": _generate_qpsk,
    "8PSK": _generate_8psk,
}


def generate_demo_iq(
    num_samples: int = 4096,
    sample_rate: float = 2_400_000,
    center_freq: float = 100_000_000,
    snr_db: float = 20.0,
    seed: int | None = None,
) -> Tuple[np.ndarray, np.ndarray, list[dict]]:
    """
    Generate complex IQ samples with 1-4 random signals mixed with AWGN.

    Returns
    -------
    i_samples : np.ndarray  (real part)
    q_samples : np.ndarray  (imaginary part)
    signal_meta : list[dict]  ground-truth signal info
    """
    rng = np.random.default_rng(seed)
    t = np.arange(num_samples) / sample_rate

    # AWGN noise
    noise_power = 10 ** (-snr_db / 10)
    noise = (
        rng.normal(0, np.sqrt(noise_power / 2), num_samples)
        + 1j * rng.normal(0, np.sqrt(noise_power / 2), num_samples)
    )

    num_signals = rng.integers(1, 5)  # 1-4 signals
    composite = noise.copy()
    signal_meta = []

    used_offsets: list[float] = []
    bw_fraction = 0.12   # each signal uses ~12% of the band

    for _ in range(num_signals):
        mod = rng.choice(DEMO_MODULATIONS)
        # Random frequency offset within the band (avoid collisions)
        for attempt in range(20):
            offset = float(rng.uniform(-sample_rate * 0.4, sample_rate * 0.4))
            if all(abs(offset - o) > sample_rate * bw_fraction for o in used_offsets):
                break
        else:
            continue  # skip if no clear spot found

        used_offsets.append(offset)
        amplitude = float(rng.uniform(0.3, 1.0))

        gen_fn = _GENERATORS[mod]
        sig = gen_fn(t, offset, sample_rate) * amplitude
        composite += sig

        signal_meta.append(
            {
                "modulation": mod,
                "center_freq": center_freq + offset,
                "offset_hz": offset,
                "bandwidth_hz": sample_rate * bw_fraction,
                "amplitude": amplitude,
            }
        )

    logger.debug("Generated %d demo signals: %s", num_signals, [s["modulation"] for s in signal_meta])

    return composite.real.tolist(), composite.imag.tolist(), signal_meta
