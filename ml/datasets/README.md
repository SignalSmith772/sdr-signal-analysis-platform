# ML Datasets

This folder stores generated training data. Files here are **git-ignored** (large binaries).

## Generated files (after running `train_model.py`)

| File | Description |
|------|-------------|
| `modulation_dataset.csv` | Feature matrix + labels (run `export_dataset.py`) |
| `X.npy` | Raw feature array, shape `(N, 12)` |
| `y.npy` | Label array, shape `(N,)` |
| `waveforms.png` | IQ waveform plots per modulation (from notebook) |
| `confusion_matrix.png` | Classifier confusion matrix (from notebook) |
| `feature_importance.png` | Random Forest feature importances (from notebook) |

## Regenerate

```bash
# From project root
python backend/scripts/export_dataset.py
```

## Feature names (12 total)

1. `spectral_entropy` — Shannon entropy of the power spectrum
2. `spectral_flatness` — Ratio of geometric to arithmetic mean of spectrum
3. `peak_to_mean_ratio` — Peak spectral power vs mean (PAPR)
4. `kurtosis_i` — 4th-order moment of I channel
5. `kurtosis_q` — 4th-order moment of Q channel
6. `skewness_i` — 3rd-order moment of I channel
7. `skewness_q` — 3rd-order moment of Q channel
8. `iq_imbalance` — Amplitude asymmetry between I and Q
9. `am_std` — Standard deviation of envelope (AM depth indicator)
10. `fm_std` — Standard deviation of instantaneous frequency
11. `pm_std` — Standard deviation of instantaneous phase derivative
12. `envelope_mean` — Mean signal envelope amplitude
