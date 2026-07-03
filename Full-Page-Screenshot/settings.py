"""
settings.py

Defines the Settings dataclass for configuration state.
"""
from dataclasses import dataclass, asdict
from constants import (
    DEFAULT_SCROLL_SPEED,
    DEFAULT_SCROLL_DELAY,
    DEFAULT_OVERLAP,
    DEFAULT_IMAGE_FORMAT,
    DEFAULT_COMPRESSION,
    DEFAULT_RETRIES,
    DEFAULT_TASKBAR_HEIGHT,
)

@dataclass
class Settings:
    """Dataclass holding all configurable application settings."""
    scroll_speed: float = DEFAULT_SCROLL_SPEED
    scroll_delay: float = DEFAULT_SCROLL_DELAY
    overlap: int = DEFAULT_OVERLAP
    image_format: str = DEFAULT_IMAGE_FORMAT
    compression: int = DEFAULT_COMPRESSION
    retries: int = DEFAULT_RETRIES
    taskbar_height: int = DEFAULT_TASKBAR_HEIGHT

    # Capture Mode
    # 1 = End of Page (uses UIA scroll position — the ONLY valid mode for completeness)
    # 2 = Time Limit  (user-configured optional limit)
    # 3 = Screenshot Limit (user-configured optional limit)
    # 5 = Manual (user presses Stop)
    capture_mode: int = 1
    mode_time_limit_min: int = 60     # Only active when capture_mode == 2
    mode_screenshot_limit: int = 5000 # Only active when capture_mode == 3

    # Export settings
    export_format: str = "PDF"           # PDF, PNG, JPEG
    pdf_page_size: str = "Auto Height"   # A4, Letter, Auto Height
    pdf_orientation: str = "Automatic"   # Portrait, Landscape, Automatic
    pdf_dpi: int = 150

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Settings':
        valid_keys = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)
