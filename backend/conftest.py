"""
backend/conftest.py — ensures `app` is importable when running pytest
from the backend/ directory directly.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
