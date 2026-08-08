"""
scripts/export_dataset.py — Export the synthetic training dataset to CSV/NPY.
Useful for inspection or loading into Jupyter notebooks.

Usage:
    python backend/scripts/export_dataset.py
"""
import sys, os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.train_model import build_dataset, DEMO_MODULATIONS

DATASET_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ml", "datasets")

FEATURE_NAMES = [
    "spectral_entropy", "spectral_flatness", "peak_to_mean",
    "kurt_i", "kurt_q", "skew_i", "skew_q", "iq_imbalance",
    "am_std", "fm_std", "pm_std", "envelope_mean",
]


if __name__ == "__main__":
    os.makedirs(DATASET_DIR, exist_ok=True)
    X, y = build_dataset()

    # Save as CSV
    df = pd.DataFrame(X, columns=FEATURE_NAMES)
    df["label"] = y
    csv_path = os.path.join(DATASET_DIR, "modulation_dataset.csv")
    df.to_csv(csv_path, index=False)
    print(f"✅ CSV saved: {csv_path}  ({len(df)} rows)")

    # Save raw arrays
    np.save(os.path.join(DATASET_DIR, "X.npy"), X)
    np.save(os.path.join(DATASET_DIR, "y.npy"), y)
    print(f"✅ NPY arrays saved to {DATASET_DIR}/")
