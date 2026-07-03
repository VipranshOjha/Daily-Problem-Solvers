"""
constants.py

Contains all application-wide constant values.
No scroll limits. No max-scroll limits. No page-height limits.
No capture limits. No timeout constants that stop scrolling.
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent

# Application defaults
DEFAULT_SCROLL_SPEED = 0.5   # seconds between scrolls
DEFAULT_SCROLL_DELAY = 1.0   # seconds to wait for rendering after scroll
DEFAULT_OVERLAP = 200         # pixels of overlap between screenshots
DEFAULT_IMAGE_FORMAT = "PNG"
DEFAULT_COMPRESSION = 1       # PNG compress level 0-9 (1 = fast, lossless)
DEFAULT_RETRIES = 3
DEFAULT_TASKBAR_HEIGHT = 48  # Windows 11 default at 1080p
