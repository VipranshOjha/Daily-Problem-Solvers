"""
chrome_controller.py

Handles interaction with the Google Chrome window.
"""
import time
import pygetwindow as gw
import keyboard

from logger import logger
from exceptions import ChromeWindowNotFoundError, AutomationError


class ChromeController:
    """Controls the Google Chrome application window."""

    def __init__(self):
        self.window = None

    # ─────────────────────────────────────────────────────────────
    # Window management
    # ─────────────────────────────────────────────────────────────

    def find_and_activate_window(self) -> None:
        """Finds the Google Chrome window and brings it to the foreground."""
        logger.info("Searching for Google Chrome window...")
        windows = gw.getWindowsWithTitle("Google Chrome")

        if not windows:
            logger.error("Google Chrome window not found.")
            raise ChromeWindowNotFoundError(
                "Could not find any window with title 'Google Chrome'. "
                "Please open Chrome and your target tabs before starting."
            )

        self.window = windows[0]

        try:
            if self.window.isMinimized:
                logger.debug("Restoring minimized Chrome window.")
                self.window.restore()

            self.window.activate()
            time.sleep(1.0)  # Wait for window to come to foreground
            logger.info(f"Activated Chrome window: {self.window.title}")

        except Exception as e:
            logger.error(f"Failed to activate Chrome window: {e}")
            raise AutomationError(f"Failed to activate Chrome window: {e}")

    def activate(self) -> None:
        """Alias for find_and_activate_window() — brings Chrome to foreground."""
        self.find_and_activate_window()

    # ─────────────────────────────────────────────────────────────
    # Window information
    # ─────────────────────────────────────────────────────────────

    def get_current_title(self) -> str:
        """Returns the current title of the active Chrome tab (window title)."""
        if self.window:
            windows = gw.getWindowsWithTitle("Google Chrome")
            for w in windows:
                if w._hWnd == self.window._hWnd:
                    return w.title
        return "Google Chrome"

    def get_hwnd(self) -> int:
        """
        Returns the Win32 HWND of the Chrome window.
        Used by ScrollEngine for UIA scroll-position reads.
        Returns 0 if window is not found.
        """
        if self.window and hasattr(self.window, '_hWnd'):
            return self.window._hWnd
        # Fallback: re-find the window
        windows = gw.getWindowsWithTitle("Google Chrome")
        if windows:
            return windows[0]._hWnd
        return 0

    # ─────────────────────────────────────────────────────────────
    # Tab switching
    # ─────────────────────────────────────────────────────────────

    def switch_next_tab(self) -> None:
        """Sends Ctrl+Tab to switch to the next tab in Chrome."""
        logger.info("Switching to next Chrome tab...")
        try:
            if self.window and not self.window.isActive:
                self.window.activate()
                time.sleep(0.5)

            keyboard.send("ctrl+tab")
            time.sleep(0.5)
            logger.debug(f"Switched tab. New title: {self.get_current_title()}")

        except Exception as e:
            logger.error(f"Failed to switch tab: {e}")
            raise AutomationError(f"Failed to switch tab: {e}")

    def next_tab(self) -> None:
        """Alias for switch_next_tab()."""
        self.switch_next_tab()
