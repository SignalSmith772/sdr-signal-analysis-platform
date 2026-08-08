# 📡 SDR Signal Analysis Platform

A production-style full-stack web application for Software-Defined Radio (SDR) signal capture, analysis, modulation classification, and reporting — built as a portfolio/resume engineering project.

![Dashboard](docs/screenshots/dashboard.png)

---

## 🏗️ Architecture Overview

```
sdr-signal-analysis-platform/
├── backend/        # FastAPI (Python) — signal processing, ML, SQLite
├── frontend/       # React + TypeScript + Tailwind CSS
├── ml/             # Scikit-learn models, training scripts, datasets
├── docs/           # Architecture docs, API reference
└── tests/          # Integration tests
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎛️ Demo Mode | Synthetic IQ data generation — no hardware needed |
| 📊 Spectrum Analyzer | FFT-based real-time frequency view |
| 🌊 Waterfall Display | Time-frequency heatmap with scrolling history |
| 🔍 Signal Detection | Automatic peak detection + band occupancy |
| 🤖 ML Classification | AM, FM, USB, LSB, CW, BPSK, QPSK, 8PSK (8 classes) |
| 📁 Session Storage | SQLite-backed analysis session history |
| 📤 Report Export | JSON/CSV report export per session |
| 🐳 Docker Support | One-command full-stack start |

---

## 🚀 Quick Start

### Option 1 — Docker (Recommended)

```bash
git clone https://github.com/yourname/sdr-signal-analysis-platform
cd sdr-signal-analysis-platform
cp .env.example .env
docker-compose up --build
```

Open [http://localhost:3000](http://localhost:3000)

---

### Option 2 — Manual Setup

#### Prerequisites
- Python 3.10+
- Node.js 18+
- pip / npm

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r ../requirements.txt
cp ../.env.example .env

# Train the ML model (creates ml/models/modulation_classifier.pkl)
python scripts/train_model.py

# Start the API server
uvicorn app.main:app --reload --port 8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

#### Frontend

```bash
cd frontend
npm install
npm start
```

App: [http://localhost:3000](http://localhost:3000)

---

## 🧪 Running Tests

```bash
cd backend
pytest app/tests/ -v
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/capture/start` | Start a capture session |
| GET  | `/api/capture/demo` | Generate synthetic IQ data |
| POST | `/api/analysis/fft` | Run FFT on IQ samples |
| POST | `/api/analysis/detect` | Detect signal peaks |
| POST | `/api/classification/classify` | Classify modulation type |
| GET  | `/api/reports/{session_id}` | Export session report |
| GET  | `/api/reports/sessions` | List all sessions |

Full API docs at `/docs` when server is running.

---

## 🤖 ML Model

The modulation classifier is trained on **synthetic IQ data** for 8 modulation types:

- AM (Amplitude Modulation)
- FM (Frequency Modulation)
- USB (Upper Sideband SSB)
- LSB (Lower Sideband SSB)
- CW (Morse Code / Carrier Wave)
- BPSK (Binary Phase Shift Keying)
- QPSK (Quadrature Phase Shift Keying)
- 8PSK (8-ary Phase Shift Keying)

**Features used:** spectral entropy, kurtosis, peak-to-average ratio, bandwidth, instantaneous AM/FM/PM features.

**Accuracy:** ~92% on held-out test set (Random Forest, 500 estimators).

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Tailwind CSS, Recharts |
| Backend | Python 3.11, FastAPI, Uvicorn |
| Signal Processing | NumPy, SciPy |
| ML | scikit-learn (Random Forest) |
| Database | SQLite (via SQLAlchemy) |
| DevOps | Docker, Docker Compose |

---

## 🗂️ Environment Variables

See `.env.example` for all options.

```env
DATABASE_URL=sqlite:///./sdr_platform.db
ML_MODEL_PATH=../ml/models/modulation_classifier.pkl
DEMO_SAMPLE_RATE=2400000
DEMO_CENTER_FREQ=100000000
CORS_ORIGINS=http://localhost:3000
```

---

## 📸 Screenshots

> Dashboard, Spectrum Analyzer, Waterfall, and Reports views available in `docs/screenshots/`.

---

## 📄 License

MIT — free for personal and commercial use.
