"""
config.py — Application settings loaded from environment / .env file.
Uses pydantic-settings for type-safe config.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    # ── Database ────────────────────────────────────────────
    DATABASE_URL: str = Field(
        default="sqlite:///./sdr_platform.db",
        description="SQLAlchemy database connection string",
    )

    # ── ML model ────────────────────────────────────────────
    ML_MODEL_PATH: str = Field(
        default="../ml/models/modulation_classifier.pkl",
        description="Path to the trained scikit-learn model",
    )

    # ── Demo / synthetic data ────────────────────────────────
    DEMO_SAMPLE_RATE: int = Field(
        default=2_400_000, description="IQ samples per second for demo data"
    )
    DEMO_CENTER_FREQ: int = Field(
        default=100_000_000, description="Center frequency for demo data (Hz)"
    )
    DEMO_NUM_SAMPLES: int = Field(
        default=4096, description="Number of IQ samples per capture block"
    )

    # ── API ─────────────────────────────────────────────────
    API_PREFIX: str = "/api"
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    DEBUG: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # allow comma-separated list for CORS_ORIGINS
        env_parse_none_str = "None"


# Singleton instance used throughout the app
settings = Settings()
