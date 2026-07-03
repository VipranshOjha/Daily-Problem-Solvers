"""
desktop_capture.py

Handles full desktop screen capture to ensure taskbar and window are visible.
"""
import mss
from PIL import Image
from logger import logger
from exceptions import CaptureError

class DesktopCapture:
    """Provides methods to capture the desktop screen."""
    
    def __init__(self):
        self.sct = mss.mss()
        # Default to monitor 1 (primary)
        self.monitor = self.sct.monitors[1]
        logger.debug(f"Initialized DesktopCapture with monitor: {self.monitor}")
        
    def capture_fullscreen(self) -> Image.Image:
        """
        Captures the entire primary monitor.
        
        Returns:
            PIL.Image.Image: The captured screenshot in RGB format.
        """
        try:
            # Grab the data
            sct_img = self.sct.grab(self.monitor)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            return img
            
        except Exception as e:
            logger.error(f"Failed to capture fullscreen: {e}")
            raise CaptureError(f"Failed to capture fullscreen: {e}")
            
    def close(self):
        """Releases mss resources."""
        self.sct.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
