"""
scripts/train_model.py — Train the modulation classification model.

Generates a large synthetic dataset of IQ signals (8 modulation types),
extracts features, and trains a Random Forest classifier.

Usage:
    python backend/scripts/train_model.py

Output:
    ml/models/modulation_classifier.pkl
"""
import sys
import os
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

# Make sure backend/app is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.sdr_service import generate_demo_iq, DEMO_MODULATIONS
from app.services.ml_service import extract_features

# ── Config ────────────────────────────────────────────────────────────────────
SAMPLES_PER_CLASS = 500      # training examples per modulation type
NUM_IQ_SAMPLES = 512          # IQ samples per example
SAMPLE_RATE = 2_400_000.0
CENTER_FREQ = 100_000_000.0
MODEL_OUTPUT = os.path.join(
    os.path.dirname(__file__), "..", "..", "ml", "models", "modulation_classifier.pkl"
)

# SNR range for training diversity (dB)
SNR_RANGE = (5, 30)


def generate_single_modulation_iq(modulation: str, n: int, fs: float, snr_db: float, seed: int):
    """
    Generate IQ samples for a single modulation type by isolating it
    from the mixed demo generator.
    """
    from app.services import sdr_service as svc
    rng = np.random.default_rng(seed)
    t = np.arange(n) / fs

    # Noise
    noise_power = 10 ** (-snr_db / 10)
    noise = (
        rng.normal(0, np.sqrt(noise_power / 2), n)
        + 1j * rng.normal(0, np.sqrt(noise_power / 2), n)
    )

    # Signal
    gen = svc._GENERATORS[modulation]
    offset = float(rng.uniform(-fs * 0.2, fs * 0.2))
    sig = gen(t, offset, fs)
    composite = sig + noise
    return composite.real.tolist(), composite.imag.tolist()


def build_dataset():
    print(f"🔧 Building dataset: {SAMPLES_PER_CLASS} samples × {len(DEMO_MODULATIONS)} classes")
    X, y = [], []

    for mod in DEMO_MODULATIONS:
        for i in range(SAMPLES_PER_CLASS):
            snr = float(np.random.uniform(*SNR_RANGE))
            seed = hash((mod, i)) % (2**31)
            try:
                i_s, q_s = generate_single_modulation_iq(
                    mod, NUM_IQ_SAMPLES, SAMPLE_RATE, snr, seed
                )
                feats = extract_features(i_s, q_s)
                X.append(feats)
                y.append(mod)
            except Exception as e:
                print(f"  ⚠️  Skipped {mod}[{i}]: {e}")

        print(f"  ✅ {mod}: {SAMPLES_PER_CLASS} examples")

    return np.array(X), np.array(y)


def train():
    os.makedirs(os.path.dirname(MODEL_OUTPUT), exist_ok=True)

    X, y = build_dataset()
    total = len(y)
    print(f"\n📊 Dataset: {total} total samples, {X.shape[1]} features")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\n🌲 Training Random Forest (500 estimators)…")
    model = RandomForestClassifier(
        n_estimators=500,
        max_depth=None,
        min_samples_split=2,
        n_jobs=-1,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    # ── Evaluation ────────────────────────────────────────────────────────────
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n✅ Test Accuracy: {acc * 100:.2f}%\n")
    print(classification_report(y_test, y_pred, target_names=sorted(DEMO_MODULATIONS)))

    # ── Save ─────────────────────────────────────────────────────────────────
    joblib.dump(model, MODEL_OUTPUT)
    print(f"\n💾 Model saved to: {MODEL_OUTPUT}")
    return acc


if __name__ == "__main__":
    train()
