"""
tests/test_api.py — Integration tests for FastAPI routes.
Uses TestClient so no live server is needed.
Run: pytest app/tests/test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.api.deps import get_db
from app.models.signal import Base

# ── In-memory SQLite for tests ────────────────────────────────────────────────
TEST_DB_URL = "sqlite:///./test_sdr.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)

client = TestClient(app)


# ── Health ────────────────────────────────────────────────────────────────────

class TestHealth:
    def test_root(self):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_health(self):
        r = client.get("/health")
        assert r.status_code == 200


# ── Capture ───────────────────────────────────────────────────────────────────

class TestCapture:
    def test_start_capture_demo(self):
        r = client.post("/api/capture/start", json={
            "mode": "demo",
            "center_freq": 100_000_000,
            "sample_rate": 2_400_000,
            "num_samples": 256,
        })
        assert r.status_code == 200
        data = r.json()
        assert "session_id" in data
        assert data["mode"] == "demo"

    def test_get_demo_iq(self):
        r = client.get("/api/capture/demo?num_samples=256")
        assert r.status_code == 200
        data = r.json()
        assert "i_samples" in data
        assert "q_samples" in data
        assert len(data["i_samples"]) == 256
        assert len(data["i_samples"]) == len(data["q_samples"])

    def test_list_sessions(self):
        r = client.get("/api/capture/sessions")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_session_not_found(self):
        r = client.get("/api/capture/99999")
        assert r.status_code == 404


# ── Analysis ──────────────────────────────────────────────────────────────────

import numpy as np

def _make_iq(n=256):
    t = np.arange(n) / 2_400_000
    iq = np.exp(1j * 2 * np.pi * 50_000 * t)
    return iq.real.tolist(), iq.imag.tolist()


class TestAnalysis:
    def test_fft_endpoint(self):
        i, q = _make_iq(256)
        r = client.post("/api/analysis/fft", json={
            "i_samples": i,
            "q_samples": q,
            "sample_rate": 2_400_000,
            "center_freq": 100_000_000,
            "fft_size": 256,
        })
        assert r.status_code == 200
        data = r.json()
        assert "frequencies" in data
        assert "powers_db" in data
        assert len(data["frequencies"]) == 256

    def test_detect_endpoint(self):
        n = 256
        freqs = np.linspace(98e6, 102e6, n).tolist()
        powers = (np.ones(n) * -80).tolist()
        powers[128] = -40.0  # inject a peak

        r = client.post("/api/analysis/detect", json={
            "frequencies": freqs,
            "powers_db": powers,
            "noise_floor_db": -80.0,
            "sample_rate": 2_400_000,
            "center_freq": 100_000_000,
        })
        assert r.status_code == 200
        data = r.json()
        assert "signals" in data
        assert "band_occupancy_pct" in data


# ── Reports ───────────────────────────────────────────────────────────────────

class TestReports:
    def test_list_sessions(self):
        r = client.get("/api/reports/sessions")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_report_not_found(self):
        r = client.get("/api/reports/99999")
        assert r.status_code == 404
