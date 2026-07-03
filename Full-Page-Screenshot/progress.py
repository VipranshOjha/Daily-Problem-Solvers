"""
progress.py

Tracks the progress of the capture session and estimates time remaining.
"""
import time

class ProgressTracker:
    """Tracks progress and calculates ETA."""
    
    def __init__(self, total_tabs: int):
        self.total_tabs = total_tabs
        self.current_tab = 0
        self.start_time = time.time()
        
    def increment(self):
        """Increments the completed tab count."""
        self.current_tab += 1

    @property
    def completed(self) -> int:
        """Alias for current_tab — number of tabs fully processed."""
        return self.current_tab
        
    def get_progress_percentage(self) -> float:
        """Returns the current progress as a float between 0 and 1."""
        if self.total_tabs == 0:
            return 0.0
        return self.current_tab / self.total_tabs
        
    def get_eta_seconds(self) -> float:
        """Estimates the remaining time in seconds."""
        if self.current_tab == 0:
            return 0.0
            
        elapsed = time.time() - self.start_time
        time_per_tab = elapsed / self.current_tab
        remaining_tabs = self.total_tabs - self.current_tab
        
        return time_per_tab * remaining_tabs
