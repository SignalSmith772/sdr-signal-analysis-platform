"""
conftest.py — pytest configuration for the backend test suite.
Adds the backend/ directory to sys.path so `app.*` imports work
without installing the package.
"""
import sys
import os

# Ensure `app` package is importable from backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
