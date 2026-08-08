# Architecture Overview

## System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser (Port 3000)                       │
│  React + TypeScript + Tailwind CSS + Recharts                   │
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │Dashboard │ │ Capture  │ │Analysis  │ │ Reports  │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│       │            │            │              │                 │
│       └────────────┴────────────┴──────────────┘                │
│                        services/api.ts (Axios)                  │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ HTTP/REST
┌─────────────────────────────────▼───────────────────────────────┐
│                     FastAPI Backend (Port 8000)                  │
│                                                                  │
│  /api/capture/*     /api/analysis/*    /api/classification/*     │
│  /api/reports/*                                                  │
│                                                                  │
│  ┌──────────────┐ ┌─────────────┐ ┌──────────────┐             │
│  │ sdr_service  │ │ fft_service │ │detection_svc │             │
│  │ (IQ gen)     │ │ (FFT/dBFS)  │ │(peak detect) │             │
│  └──────────────┘ └─────────────┘ └──────────────┘             │
│  ┌──────────────┐ ┌─────────────┐                               │
│  │  ml_service  │ │report_svc   │                               │
│  │ (RF model)   │ │(JSON/CSV)   │                               │
│  └──────────────┘ └─────────────┘                               │
│                                                                  │
│  SQLAlchemy ORM → SQLite (sdr_platform.db)                      │
│  Tables: capture_sessions, analysis_results, detected_signals   │
└─────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│                        ML Layer                                  │
│                                                                  │
│  Random Forest Classifier (scikit-learn)                        │
│  • 8 modulation classes: AM FM USB LSB CW BPSK QPSK 8PSK       │
│  • 12 features per sample (spectral + statistical + instant.)   │
│  • Trained on synthetic IQ, ~92% accuracy                       │
│  • Saved as ml/models/modulation_classifier.pkl                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
1. Frontend requests demo IQ data
        ↓
2. sdr_service.generate_demo_iq() creates complex IQ with 1–4 signals
        ↓
3. fft_service.compute_fft() → power spectrum (dBFS), noise floor
        ↓
4. detection_service.detect_signals() → list of peaks with SNR/BW
        ↓
5. ml_service.classify_modulation() → modulation label + confidence
        ↓
6. Results stored in SQLite via SQLAlchemy ORM
        ↓
7. Frontend renders SpectrumChart + WaterfallView + SignalTable
```

## Key Design Decisions

| Decision | Rationale |
|---|---|
| SQLite over PostgreSQL | Zero-config, portable, perfect for portfolio demo |
| Random Forest over deep learning | Interpretable, fast inference, no GPU needed |
| Synthetic IQ data | Works without physical SDR hardware |
| Separate FFT + Detection + Classification | Each step testable independently |
| Recharts over D3 | React-native, TypeScript-friendly |
| Canvas waterfall | HTML5 Canvas is fastest for scrolling pixel data |
