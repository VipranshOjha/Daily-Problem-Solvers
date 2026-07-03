"""
system_metrics.py

Provides telemetry for CPU and Memory usage via psutil.
"""
import psutil
import os

class SystemMetrics:
    """Tracks CPU and Memory usage of the current process."""
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        # First call to cpu_percent initializes the baseline
        self.process.cpu_percent(interval=None)
        
    def get_cpu_percent(self) -> float:
        """Returns the CPU usage percentage of the application."""
        return self.process.cpu_percent(interval=None)
        
    def get_memory_mb(self) -> float:
        """Returns the memory usage of the application in MB."""
        return self.process.memory_info().rss / (1024 * 1024)

# Global singleton
system_metrics = SystemMetrics()
