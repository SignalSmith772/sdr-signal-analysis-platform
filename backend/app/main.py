"""
main.py — FastAPI application entry point.
Registers all routers, configures CORS, and initialises the database.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import capture, analysis, classification, reports
from app.models import signal  # noqa — ensures tables are created
from app.utils.logging import configure_logging

# ── Database bootstrap ───────────────────────────────────────────────────────
from sqlalchemy import create_engine
from app.models.signal import Base

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite-specific
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables on startup."""
    configure_logging()
    Base.metadata.create_all(bind=engine)
    logging.info("✅ Database tables created / verified.")
    yield
    logging.info("🛑 Application shutdown.")


# ── App factory ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="SDR Signal Analysis Platform",
    description=(
        "REST API for SDR IQ data capture, FFT spectrum analysis, "
        "signal detection, and ML-based modulation classification."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(capture.router, prefix=f"{settings.API_PREFIX}/capture", tags=["Capture"])
app.include_router(analysis.router, prefix=f"{settings.API_PREFIX}/analysis", tags=["Analysis"])
app.include_router(classification.router, prefix=f"{settings.API_PREFIX}/classification", tags=["Classification"])
app.include_router(reports.router, prefix=f"{settings.API_PREFIX}/reports", tags=["Reports"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "SDR Signal Analysis Platform API"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "version": "1.0.0"}
