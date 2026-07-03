"""
utils.py

General utility functions.
"""
import time

def format_time(seconds: float) -> str:
    """Formats seconds into a human readable MM:SS string."""
    mins, secs = divmod(int(seconds), 60)
    return f"{mins:02d}:{secs:02d}"
