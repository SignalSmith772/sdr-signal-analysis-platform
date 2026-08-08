# ML Models

This folder stores trained model binaries. Files are **git-ignored**.

## Files

| File | Description |
|------|-------------|
| `modulation_classifier.pkl` | Trained Random Forest (joblib format) |

## Generate the model

```bash
# From project root — takes ~60 seconds
python backend/scripts/train_model.py
```

## Model details

| Property | Value |
|----------|-------|
| Algorithm | Random Forest (scikit-learn) |
| Estimators | 500 trees |
| Classes | AM, FM, USB, LSB, CW, BPSK, QPSK, 8PSK |
| Features | 12 (spectral + statistical + instantaneous) |
| Training samples | 4000 (500 per class) |
| Test accuracy | ~92% |
| Inference time | <5 ms per sample |

## Loading the model

```python
import joblib
model = joblib.load('ml/models/modulation_classifier.pkl')

# Predict
features = extract_features(i_samples, q_samples).reshape(1, -1)
label = model.predict(features)[0]
proba = model.predict_proba(features)[0]
```
