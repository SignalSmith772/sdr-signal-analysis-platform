"""
tests/integration/test_full_pipeline.py
End-to-end pipeline test: demo IQ → FFT → detect → classify → report.
Requires the backend server to be running on localhost:8000.

Run:
    pytest tests/integration/test_full_pipeline.py -v
"""
import pytest
import httpx

BASE = "http://localhost:8000"


@pytest.fixture(scope="module")
def client():
    return httpx.Client(base_url=BASE, timeout=30)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_full_pipeline(client):
    # 1) Demo IQ
    r = client.get("/api/capture/demo", params={"num_samples": 512})
    assert r.status_code == 200
    iq = r.json()
    session_id = iq["session_id"]
    assert len(iq["i_samples"]) == 512

    # 2) FFT
    r = client.post("/api/analysis/fft", json={
        "i_samples": iq["i_samples"],
        "q_samples": iq["q_samples"],
        "sample_rate": iq["sample_rate"],
        "center_freq": iq["center_freq"],
        "fft_size": 512,
        "session_id": session_id,
    })
    assert r.status_code == 200
    fft = r.json()
    assert "frequencies" in fft
    assert fft["peak_power_db"] > fft["noise_floor_db"]

    # 3) Detect
    r = client.post("/api/analysis/detect", json={
        "frequencies": fft["frequencies"],
        "powers_db": fft["powers_db"],
        "noise_floor_db": fft["noise_floor_db"],
        "sample_rate": iq["sample_rate"],
        "center_freq": iq["center_freq"],
    })
    assert r.status_code == 200
    det = r.json()
    assert "signals" in det
    assert 0 <= det["band_occupancy_pct"] <= 100

    # 4) Classify (if model exists)
    r = client.post("/api/classification/classify", json={
        "i_samples": iq["i_samples"][:256],
        "q_samples": iq["q_samples"][:256],
        "sample_rate": iq["sample_rate"],
    })
    if r.status_code == 200:
        cls = r.json()
        assert "modulation" in cls
        assert 0 <= cls["confidence"] <= 1
    else:
        # Model not trained yet — acceptable in CI
        assert r.status_code == 503

    # 5) Report
    r = client.get(f"/api/reports/{session_id}")
    assert r.status_code == 200
    report = r.json()
    assert report["session"]["id"] == session_id
