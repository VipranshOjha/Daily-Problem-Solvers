"""
capture_modes.py

Defines the available capture modes to handle unlimited scrolling pages.
"""
from enum import IntEnum

class CaptureMode(IntEnum):
    END_OF_PAGE = 1
    TIME_LIMIT = 2
    SCREENSHOT_LIMIT = 3
    SIZE_LIMIT = 4
    MANUAL = 5
