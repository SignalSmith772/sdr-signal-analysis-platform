"""
utils/validators.py — Request validation helpers.
"""
from fastapi import HTTPException


def validate_iq_samples(i_samples: list, q_samples: list, min_len: int = 64) -> None:
    """Raise HTTPException if IQ samples are invalid."""
    if len(i_samples) != len(q_samples):
        raise HTTPException(
            status_code=422,
            detail=f"I and Q sample lists must have equal length "
                   f"(got {len(i_samples)} vs {len(q_samples)}).",
        )
    if len(i_samples) < min_len:
        raise HTTPException(
            status_code=422,
            detail=f"Need at least {min_len} samples (got {len(i_samples)}).",
        )
