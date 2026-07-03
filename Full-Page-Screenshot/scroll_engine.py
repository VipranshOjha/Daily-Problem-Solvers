"""
scroll_engine.py

Handles scrolling the Chrome page and — critically — reading the TRUE
physical scroll position from the OS via Windows UI Automation (UIA).

DESIGN PRINCIPLES
─────────────────
• Scrolling never stops due to a timer, counter, image hash, or any heuristic.
• The ONLY stop condition is: Chrome's OS-reported scroll position is at 100%
  AND a confirmation scroll attempt leaves it at 100%.
• UIA (pywinauto) reads Chrome's IScrollProvider.CurrentVerticalScrollPercent
  directly from the Windows accessibility layer — no JavaScript, no clipboard,
  no address bar, no DevTools.
"""
import time
import keyboard
import pyautogui

from config import config_manager
from logger import logger
from exceptions import AutomationError

# ─────────────────────────────────────────────────────────────────────────────
# UIA availability check (pywinauto must be installed)
# ─────────────────────────────────────────────────────────────────────────────

try:
    from pywinauto import Desktop as _UIA_Desktop
    _UIA_AVAILABLE = True
    logger.info("pywinauto loaded — UIA scroll position detection ACTIVE.")
except ImportError:
    _UIA_AVAILABLE = False
    logger.warning(
        "pywinauto is NOT installed. UIA scroll detection is unavailable.\n"
        "Install it with: pip install pywinauto\n"
        "Without it, End-of-Page capture will continue indefinitely until "
        "the user presses Stop."
    )


class ScrollEngine:
    """
    Provides scrolling and OS-level scroll-position reading for Chrome.

    Scroll Position Return Codes
    ────────────────────────────
    get_scroll_percent() returns:
        0.0 – 100.0  : Actual vertical scroll percentage (100.0 = physical bottom)
        -1.0         : Page is not scrollable (content fits in viewport — stop)
        -2.0         : UIA unavailable or read failed (cannot determine — keep scrolling)
    """

    def __init__(self):
        self.config = config_manager.settings

    # ─────────────────────────────────────────────────────────────
    # Scrolling
    # ─────────────────────────────────────────────────────────────

    def scroll_down(self) -> None:
        """
        Scrolls down one viewport using the Page Down key.
        Waits for lazy-loaded content to render before returning.
        """
        try:
            logger.debug("Scrolling down (Page Down)...")
            keyboard.send("page down")
            time.sleep(self.config.scroll_delay)
        except Exception as e:
            logger.error(f"Failed to scroll down: {e}")
            raise AutomationError(f"Failed to scroll down: {e}")

    def scroll_to_top(self) -> None:
        """Scrolls immediately to the absolute top of the page (Ctrl+Home)."""
        try:
            logger.debug("Scrolling to top (Ctrl+Home)...")
            keyboard.send("ctrl+home")
            time.sleep(self.config.scroll_delay)
        except Exception as e:
            logger.error(f"Failed to scroll to top: {e}")
            raise AutomationError(f"Failed to scroll to top: {e}")

    def smooth_scroll(self) -> None:
        """
        Fallback smooth scrolling via mouse wheel for pages where Page Down
        triggers navigation instead of page scrolling.
        """
        try:
            logger.debug("Smooth scrolling (mouse wheel)...")
            for _ in range(10):
                pyautogui.scroll(-200)
                time.sleep(0.05)
            time.sleep(self.config.scroll_delay)
        except Exception as e:
            logger.error(f"Failed to smooth scroll: {e}")
            raise AutomationError(f"Failed to smooth scroll: {e}")

    # ─────────────────────────────────────────────────────────────
    # UIA scroll position — the authoritative stop condition
    # ─────────────────────────────────────────────────────────────

    def get_scroll_percent(self, hwnd: int) -> float:
        """
        Reads Chrome's vertical scroll percentage via Windows UI Automation.

        This uses the OS accessibility layer (IScrollProvider) to query Chrome's
        actual scroll state. There is NO JavaScript execution, NO clipboard
        interaction, NO address bar interaction, and NO DevTools involvement.
        This is a pure OS-level read.

        Parameters
        ──────────
        hwnd : int
            The Win32 window handle of the Chrome window (from ChromeController.get_hwnd()).

        Returns
        ───────
        float
            0.0 – 100.0  Vertical scroll percentage. 100.0 = physically at bottom.
            -1.0         Page reports itself as not scrollable (fits in viewport).
            -2.0         UIA unavailable or the scroll pattern could not be read.
                         When -2.0, the orchestrator MUST continue scrolling.
        """
        if not _UIA_AVAILABLE:
            return -2.0

        if not hwnd:
            logger.debug("get_scroll_percent: hwnd is 0, cannot query UIA.")
            return -2.0

        try:
            desktop = _UIA_Desktop(backend='uia')
            win = desktop.window(handle=hwnd)

            # Chrome exposes its active web content as a UIA 'Document' element.
            # This is the scrollable container we need to query.
            docs = win.descendants(control_type='Document')

            if not docs:
                # No Document element found — could be a PDF viewer, new tab page, etc.
                logger.debug("get_scroll_percent: No UIA Document element found.")
                return -2.0

            # Use the first (foremost) Document element — the active tab's content.
            doc = docs[0]
            try:
                iface = doc.iface_scroll
                pct = float(iface.CurrentVerticalScrollPercent)
                logger.debug(f"UIA scroll position: {pct:.2f}%")
                return pct
                # pct == -1.0 → UIA reports element is not scrollable
                # pct 0-100   → actual scroll percentage

            except Exception as e:
                # Element found but does not support IScrollProvider
                logger.debug(f"IScrollProvider not supported on Document: {e}")
                return -2.0

        except Exception as e:
            logger.debug(f"UIA scroll read error: {e}")
            return -2.0

    def is_at_physical_bottom(self, hwnd: int) -> bool:
        """
        Returns True only when the OS confirms Chrome is at the physical bottom.

        -1.0 → Not scrollable at all (page fits in viewport) → treat as bottom.
        100.0+ → Scroll position maxed out → at bottom.

        Does NOT return True for -2.0 (UIA unavailable) — in that case the
        orchestrator must keep scrolling.
        """
        pct = self.get_scroll_percent(hwnd)
        if pct == -1.0:
            return True   # Page cannot scroll at all
        if pct >= 99.9:
            return True   # OS reports scroll is at 100%
        return False
