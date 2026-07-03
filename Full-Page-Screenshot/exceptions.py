"""
exceptions.py

Custom exceptions for the application.
"""

class ChromeCaptureError(Exception):
    """Base exception for Full-Page-Screenshot."""
    pass

class ChromeWindowNotFoundError(ChromeCaptureError):
    """Raised when the Google Chrome window cannot be found."""
    pass

class AutomationError(ChromeCaptureError):
    """Raised when a desktop automation action fails."""
    pass

class CaptureError(ChromeCaptureError):
    """Raised when capturing a screenshot fails."""
    pass

class StitchingError(ChromeCaptureError):
    """Raised when image stitching fails."""
    pass

class InvalidConfigurationError(ChromeCaptureError):
    """Raised when the configuration is invalid."""
    pass
