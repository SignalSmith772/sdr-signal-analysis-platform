"""
utils/logging.py — Configure application-wide logging format.
"""
import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """Set up structured console logging for the FastAPI app."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    # Quiet down noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
