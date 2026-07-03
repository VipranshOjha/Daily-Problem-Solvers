import sys
import tkinter as tk
from tkinter import messagebox
from gui import FullPageScreenshotGUI
from logger import logger
import pygetwindow as gw

def check_first_run():
    """First run experience checks."""
    try:
        windows = gw.getWindowsWithTitle("Google Chrome")
        if not windows:
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning(
                "Chrome Not Found",
                "Google Chrome does not appear to be running. Please open Chrome and your target tabs before starting the capture."
            )
            root.destroy()
    except Exception as e:
        logger.warning(f"First run check failed: {e}")

def main() -> None:
    """
    Main entry point for the Full-Page-Screenshot application.
    This will initialize the GUI and start the main event loop.
    """
    try:
        logger.info("Initializing Full-Page-Screenshot GUI...")
        check_first_run()
        app = FullPageScreenshotGUI()
        app.run()
    except Exception as e:
        logger.critical(f"Application crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
