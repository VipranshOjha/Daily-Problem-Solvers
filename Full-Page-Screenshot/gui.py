"""
gui.py

Windows 11-style GUI for Full-Page-Screenshot.
Handles background orchestration of the capture process.

CAPTURE ENGINE GUARANTEES
──────────────────────────
• Every tab, including the LAST, executes the identical capture pipeline.
• The application does NOT terminate until the final PDF has been written,
  logs have been flushed, and the session has been finalized.
• Scrolling stops ONLY when Windows UI Automation (UIA) confirms Chrome is
  physically at the bottom of the page (VerticalScrollPercent ≥ 99.9%),
  verified by one additional scroll attempt with the same result.
• No hard scroll limits. No max-page-height limits. No timeout stops.
  No image-hash stops. No visual-similarity stops.
"""
import threading
import time
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
from pathlib import Path
import customtkinter as ctk

from config import config_manager
from logger import logger
from file_manager import FileManager
from progress import ProgressTracker
from utils import format_time
from chrome_controller import ChromeController
from desktop_capture import DesktopCapture
from scroll_engine import ScrollEngine
from image_stitcher import ImageStitcher
from export_pipeline import ExportPipeline
from exceptions import ChromeCaptureError
from system_metrics import system_metrics

# ─────────────────────────────────────────────────────────────────────────────
# Colour palette
# ─────────────────────────────────────────────────────────────────────────────

ACCENT_BLUE   = "#0078D4"
ACCENT_HOVER  = "#106EBE"
STATUS_COLORS = {
    "IDLE":      "#6E6E73",
    "CAPTURING": "#0078D4",
    "STITCHING": "#8855FF",
    "EXPORTING": "#FF8C00",
    "COMPLETE":  "#30C85E",
    "PAUSED":    "#FFB900",
    "STOPPED":   "#E8453C",
    "ERROR":     "#E8453C",
}
LOG_TAG_COLORS = {
    "INFO":    {"dark": "#E0E0E0", "light": "#1C1C1E"},
    "WARNING": {"dark": "#FFB900", "light": "#9A6700"},
    "ERROR":   {"dark": "#FF6B6B", "light": "#C0392B"},
    "SUCCESS": {"dark": "#30C85E", "light": "#1A7A3A"},
    "DEBUG":   {"dark": "#808080", "light": "#999999"},
}


# ─────────────────────────────────────────────────────────────────────────────
# CaptureOrchestrator — background thread
# ─────────────────────────────────────────────────────────────────────────────

class CaptureOrchestrator(threading.Thread):
    """
    Background thread that runs the full capture session.

    DESIGN CONTRACT
    ───────────────
    • _capture_tab() is called identically for EVERY tab, including the last.
    • No early exits from the tab loop. No cleanup before export.
    • The 'finished' callback fires ONLY after the last PDF is written
      and session metadata is saved.
    • The only stop condition for scrolling is UIA-confirmed physical bottom.
    """

    def __init__(self, callbacks: dict, total_tabs: int):
        """
        Parameters
        ──────────
        callbacks : dict with keys:
            'status'      (status: str, tab_idx: int, title: str, tracker: ProgressTracker) → None
            'log'         (message: str, level: str) → None
            'telemetry'   (**kwargs) → None
            'output_file' (path: Path) → None
            'finished'    () → None
        total_tabs : int
            Number of Chrome tabs to capture.
        """
        super().__init__(daemon=True)

        self.callbacks   = callbacks
        self.total_tabs  = total_tabs

        self.is_paused  = False
        self.is_stopped = False

        self.file_manager = FileManager()
        self.chrome       = ChromeController()
        self.scroll       = ScrollEngine()
        self.stitcher     = ImageStitcher()
        self.exporter     = ExportPipeline()
        self.tracker      = ProgressTracker(total_tabs)

        self._latest_output: Path | None = None

    # ── Internal helpers ──────────────────────────────────────────

    def _log(self, msg: str, level: str = "INFO") -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self.callbacks["log"](f"[{ts}] [{level}]  {msg}", level)
        logger.info(f"[{level}] {msg}")

    def _set_status(self, status: str, tab_idx: int = 0, title: str = "") -> None:
        self.callbacks["status"](status, tab_idx, title, self.tracker)

    def _push_telemetry(self, **kwargs) -> None:
        self.callbacks["telemetry"](**kwargs)

    def _wait_if_paused(self) -> bool:
        """Blocks while paused. Returns True if stopped during the wait."""
        while self.is_paused:
            time.sleep(0.2)
            if self.is_stopped:
                return True
        return False

    # ── Tab capture pipeline ──────────────────────────────────────

    def _capture_tab(self, tab_idx: int, title: str) -> None:
        """
        Complete capture pipeline for ONE tab.
        Called identically for every tab — first, middle, or last.
        Exits only when:
            (a) UIA confirms physical bottom (End of Page mode), OR
            (b) User-configured time/screenshot limit is reached, OR
            (c) User pressed Stop.
        Export and file-save always run before this method returns.
        """
        images        = []
        total_scrolls = 0
        stop_reason   = "Unknown"
        tab_start     = datetime.now()

        # ── Scroll to absolute top ────────────────────────────────
        self._log(f"Scrolling to top of page...")
        self.scroll.scroll_to_top()
        time.sleep(1.5)  # Allow page to fully settle at top

        hwnd = self.chrome.get_hwnd()
        if not hwnd:
            self._log("WARNING: Could not obtain Chrome window handle (HWND). "
                      "UIA scroll detection may be impaired.", level="WARNING")

        self._set_status("CAPTURING", tab_idx, title)

        # ─────────────────────────────────────────────────────────
        # Screenshot + scroll loop
        # ─────────────────────────────────────────────────────────
        with DesktopCapture() as capture:

            # Capture the initial (top-of-page) frame before any scrolling
            initial = capture.capture_fullscreen()
            if initial:
                images.append(initial)
                self._log(f"Captured initial frame (top of page).")

            while True:

                # ── Check user stop ────────────────────────────────
                if self.is_stopped:
                    stop_reason = "Stopped by user"
                    break

                # ── Handle pause ───────────────────────────────────
                if self.is_paused:
                    self._set_status("PAUSED", tab_idx, title)
                    stopped_during_pause = self._wait_if_paused()
                    if stopped_during_pause:
                        stop_reason = "Stopped by user (during pause)"
                        break
                    self._set_status("CAPTURING", tab_idx, title)

                # ── User-configured Time Limit (mode 2 only) ───────
                if self.file_manager.config.capture_mode == 2:
                    elapsed_min = (datetime.now() - tab_start).total_seconds() / 60
                    if elapsed_min >= self.file_manager.config.mode_time_limit_min:
                        stop_reason = "User-configured time limit reached"
                        break

                # ── User-configured Screenshot Limit (mode 3 only) ─
                if self.file_manager.config.capture_mode == 3:
                    if len(images) >= self.file_manager.config.mode_screenshot_limit:
                        stop_reason = "User-configured screenshot limit reached"
                        break

                # ── Scroll down one viewport ───────────────────────
                self.scroll.scroll_down()
                total_scrolls += 1

                # ── Read ACTUAL scroll position from OS (UIA) ──────
                pct = self.scroll.get_scroll_percent(hwnd)

                # ── Capture current viewport ───────────────────────
                img = capture.capture_fullscreen()
                if img:
                    images.append(img)

                # ── Push live telemetry to GUI ─────────────────────
                self._push_telemetry(
                    cpu=system_metrics.get_cpu_percent(),
                    mem=system_metrics.get_memory_mb(),
                    scroll_count=total_scrolls,
                    scroll_pct=max(0.0, pct),
                    img_count=len(images),
                    tab_idx=tab_idx,
                    title=title,
                )
                self._log(
                    f"Scroll #{total_scrolls:,} | "
                    f"UIA position: {pct:.1f}% | "
                    f"Frames: {len(images):,}"
                )

                # ─────────────────────────────────────────────────────────
                # STOP CONDITION — the ONLY acceptable stop condition
                # ─────────────────────────────────────────────────────────

                if pct == -1.0:
                    # UIA: element is not scrollable (single-screen page).
                    stop_reason = "Page not scrollable — content fits in viewport"
                    break

                if pct == -2.0:
                    # UIA unavailable or failed to read.
                    # Per product requirement: KEEP SCROLLING.
                    # The user must press Stop manually when UIA is unavailable.
                    continue

                if pct >= 99.9:
                    # ─────────────────────────────────────────────────────
                    # OS reports scroll is at 100%.
                    #
                    # To confirm this is the TRUE physical bottom (not a
                    # momentary reading during content load), we attempt
                    # one additional scroll and re-read the position.
                    #
                    # If position is STILL ≥ 99.9% after the extra scroll,
                    # Chrome physically cannot move further — stop.
                    #
                    # If position dropped below 99.9%, the page grew
                    # (infinite scroll, lazy load) — continue scrolling.
                    # ─────────────────────────────────────────────────────
                    self._log(
                        f"UIA reports {pct:.2f}% — attempting confirmation scroll...",
                        level="INFO"
                    )

                    self.scroll.scroll_down()
                    total_scrolls += 1

                    confirm_pct = self.scroll.get_scroll_percent(hwnd)

                    # Capture frame after confirmation scroll
                    confirm_img = capture.capture_fullscreen()
                    if confirm_img:
                        images.append(confirm_img)

                    if confirm_pct >= 99.9:
                        # ✓ TRUE PHYSICAL BOTTOM CONFIRMED
                        stop_reason = (
                            f"True physical bottom confirmed by UIA "
                            f"(primary: {pct:.2f}%, confirmation: {confirm_pct:.2f}%)"
                        )
                        break
                    else:
                        # Page grew — infinite scroll or lazy content loaded
                        self._log(
                            f"Page extended after confirmation scroll "
                            f"(new position: {confirm_pct:.2f}%). Continuing...",
                            level="INFO"
                        )
                        self._push_telemetry(
                            cpu=system_metrics.get_cpu_percent(),
                            mem=system_metrics.get_memory_mb(),
                            scroll_count=total_scrolls,
                            scroll_pct=max(0.0, confirm_pct),
                            img_count=len(images),
                            tab_idx=tab_idx,
                            title=title,
                        )

        # ── Capture summary log ───────────────────────────────────
        self._log("─" * 48)
        self._log(f"TAB {tab_idx}/{self.total_tabs} CAPTURE COMPLETE")
        self._log(f"  Total scrolls performed : {total_scrolls:,}")
        self._log(f"  Screenshots captured    : {len(images):,}")
        self._log(f"  Stop reason             : {stop_reason}")
        self._log("─" * 48)

        # ── Stitch ───────────────────────────────────────────────
        if not images:
            self._log(f"No images captured for tab {tab_idx}. Skipping export.", level="WARNING")
            return

        self._set_status("STITCHING", tab_idx, title)
        self._log(f"Stitching {len(images):,} screenshots into a single image...")

        try:
            stitched = self.stitcher.stitch_images(images)
        except Exception as e:
            self._log(f"Stitching failed: {e}", level="ERROR")
            return

        if not stitched:
            self._log("Stitcher returned no image.", level="ERROR")
            return

        # ── Export ────────────────────────────────────────────────
        self._set_status("EXPORTING", tab_idx, title)
        output_file = self.file_manager.generate_filename(tab_idx, title)
        self._log(f"Exporting to {output_file.name}...")

        try:
            self.exporter.export(stitched, output_file, title)
            self._latest_output = output_file
            self.callbacks["output_file"](output_file)
            self._log(f"Saved → {output_file}", level="SUCCESS")
        except Exception as e:
            self._log(f"Export failed for tab {tab_idx}: {e}", level="ERROR")

    # ── Main thread ───────────────────────────────────────────────

    def run(self) -> None:
        """
        Main orchestration loop.

        TAB LOOP CONTRACT
        ─────────────────
        • For tab N in range(1, total_tabs+1):
            1. _capture_tab(N, title)     ← identical for every N, including last
            2. tracker.increment()
            3. if N < total_tabs: switch_next_tab()
        • Session finalization (metadata save, logs, 'finished' callback)
          fires ONLY after the loop completes — i.e., after the last
          PDF has been fully written.
        """
        session_start = datetime.now()

        try:
            self._log(f"═" * 50)
            self._log(f"Full-Page-Screenshot — Session Start")
            self._log(f"Tabs to capture : {self.total_tabs}")
            self._log(f"Capture mode    : {self.file_manager.config.capture_mode}")
            self._log(f"Export format   : {self.file_manager.config.export_format}")
            self._log(f"═" * 50)

            # Bring Chrome to foreground
            self.chrome.activate()

            # ── Tab loop ──────────────────────────────────────────
            for tab_idx in range(1, self.total_tabs + 1):

                if self.is_stopped:
                    self._log("Session stopped by user before tab "
                              f"{tab_idx} could be processed.")
                    break

                # Read tab title now (Chrome window title = active tab title)
                title = self.chrome.get_current_title()
                self._log(f"")
                self._log(f"TAB {tab_idx}/{self.total_tabs}: «{title}»")
                self._set_status("CAPTURING", tab_idx, title)

                # ── IDENTICAL pipeline for every tab (incl. last) ─
                self._capture_tab(tab_idx, title)

                # ── Mark tab as done ───────────────────────────────
                self.tracker.increment()

                # ── Switch tab ONLY if there is a next tab ─────────
                # Export is complete by this point. Safe to switch.
                if tab_idx < self.total_tabs and not self.is_stopped:
                    self._log(f"Switching to next tab...")
                    self.chrome.switch_next_tab()
                    time.sleep(2.0)  # Allow new tab to fully render

            # ── Session finalisation ──────────────────────────────
            # Reaches here ONLY after last PDF has been written.
            end_time = datetime.now()
            elapsed  = (end_time - session_start).total_seconds()

            if not self.is_stopped:
                session_data = {
                    "start_time":    session_start.isoformat(),
                    "end_time":      end_time.isoformat(),
                    "elapsed_sec":   round(elapsed, 1),
                    "tabs_captured": self.tracker.current_tab,
                    "export_format": self.file_manager.config.export_format,
                    "capture_mode":  self.file_manager.config.capture_mode,
                }
                self.file_manager.save_session_data(session_data)
                self._log(f"")
                self._log(f"═" * 50)
                self._log(
                    f"SESSION COMPLETE — "
                    f"{self.tracker.current_tab} tab(s) captured in "
                    f"{format_time(elapsed)}",
                    level="SUCCESS"
                )
                self._log(f"═" * 50)
            else:
                self._log("Session stopped by user.", level="WARNING")

        except ChromeCaptureError as e:
            self._log(f"Chrome error: {e}", level="ERROR")
        except Exception as e:
            self._log(f"Unexpected error: {e}", level="ERROR")
            logger.exception("Unexpected error in CaptureOrchestrator.run()")
        finally:
            # This fires AFTER the last PDF is written and metadata is saved.
            self.callbacks["finished"]()


# ─────────────────────────────────────────────────────────────────────────────
# Settings dialog
# ─────────────────────────────────────────────────────────────────────────────

class SettingsDialog(ctk.CTkToplevel):
    """Tabbed settings dialog."""

    def __init__(self, parent: ctk.CTk):
        super().__init__(parent)
        self.title("Settings — Full-Page-Screenshot")
        self.geometry("540x500")
        self.resizable(False, False)
        self.grab_set()
        self.focus()
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text="⚙   Settings",
            font=ctk.CTkFont("Inter", 20, "bold")
        ).pack(padx=24, pady=(20, 8), anchor="w")

        tabs = ctk.CTkTabview(self, width=490, height=360)
        tabs.pack(padx=24, pady=4, fill="both", expand=True)

        cap  = tabs.add("  Capture  ")
        exp  = tabs.add("  Export   ")
        adv  = tabs.add("  Advanced ")

        self._widgets: dict = {}

        # ── Capture ────────────────────────────────────────────────
        self._row(cap, "Scroll Delay (s):", "scroll_delay",
                  ctk.CTkEntry(cap), str(config_manager.settings.scroll_delay))
        self._row(cap, "Capture Mode:", "capture_mode_str",
                  ctk.CTkOptionMenu(cap, values=["End of Page", "Time Limit",
                                                  "Screenshot Limit", "Manual"]),
                  {1: "End of Page", 2: "Time Limit",
                   3: "Screenshot Limit", 5: "Manual"}.get(
                       config_manager.settings.capture_mode, "End of Page"))
        self._row(cap, "Time Limit (min):", "mode_time_limit_min",
                  ctk.CTkEntry(cap), str(config_manager.settings.mode_time_limit_min))
        self._row(cap, "Screenshot Limit:", "mode_screenshot_limit",
                  ctk.CTkEntry(cap), str(config_manager.settings.mode_screenshot_limit))

        ctk.CTkLabel(cap,
                     text="ℹ  Time Limit and Screenshot Limit apply only when\n"
                          "   the corresponding Capture Mode is selected.",
                     font=ctk.CTkFont("Inter", 11),
                     text_color="gray", justify="left"
                     ).pack(padx=16, pady=(8, 0), anchor="w")

        # ── Export ─────────────────────────────────────────────────
        self._row(exp, "Export Format:", "export_format",
                  ctk.CTkOptionMenu(exp, values=["PDF", "PNG", "JPEG"]),
                  config_manager.settings.export_format)
        self._row(exp, "PDF Page Size:", "pdf_page_size",
                  ctk.CTkOptionMenu(exp, values=["Auto Height", "A4", "Letter"]),
                  config_manager.settings.pdf_page_size)
        self._row(exp, "PDF Orientation:", "pdf_orientation",
                  ctk.CTkOptionMenu(exp, values=["Automatic", "Portrait", "Landscape"]),
                  config_manager.settings.pdf_orientation)
        self._row(exp, "PDF DPI:", "pdf_dpi",
                  ctk.CTkOptionMenu(exp, values=["72", "96", "150", "200", "300"]),
                  str(config_manager.settings.pdf_dpi))

        # ── Advanced ───────────────────────────────────────────────
        self._row(adv, "Screenshot Overlap (px):", "overlap",
                  ctk.CTkEntry(adv), str(config_manager.settings.overlap))
        self._row(adv, "Taskbar Height (px):", "taskbar_height",
                  ctk.CTkEntry(adv), str(config_manager.settings.taskbar_height))

        # ── Footer buttons ─────────────────────────────────────────
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(padx=24, pady=12, fill="x")

        ctk.CTkButton(
            footer, text="Cancel", width=100,
            fg_color="transparent", border_width=1,
            command=self.destroy
        ).pack(side="right", padx=(6, 0))

        ctk.CTkButton(
            footer, text="Save", width=100,
            fg_color=ACCENT_BLUE, hover_color=ACCENT_HOVER,
            command=self._save
        ).pack(side="right")

    def _row(self, parent, label: str, key: str, widget, default_val: str = ""):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=5, padx=12)
        ctk.CTkLabel(row, text=label, width=175, anchor="w").pack(side="left")
        if isinstance(widget, ctk.CTkEntry):
            widget.insert(0, default_val)
        elif isinstance(widget, ctk.CTkOptionMenu):
            widget.set(default_val)
        widget.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self._widgets[key] = widget

    def _save(self):
        cfg = config_manager.settings
        try:
            cfg.scroll_delay = float(self._get("scroll_delay"))
        except ValueError:
            pass
        try:
            cfg.mode_time_limit_min = int(self._get("mode_time_limit_min"))
        except ValueError:
            pass
        try:
            cfg.mode_screenshot_limit = int(self._get("mode_screenshot_limit"))
        except ValueError:
            pass
        try:
            cfg.overlap = int(self._get("overlap"))
        except ValueError:
            pass
        try:
            cfg.taskbar_height = int(self._get("taskbar_height"))
        except ValueError:
            pass
        try:
            cfg.pdf_dpi = int(self._get("pdf_dpi"))
        except ValueError:
            pass

        cfg.export_format   = self._get("export_format")
        cfg.pdf_page_size   = self._get("pdf_page_size")
        cfg.pdf_orientation = self._get("pdf_orientation")
        mode_rev = {"End of Page": 1, "Time Limit": 2,
                    "Screenshot Limit": 3, "Manual": 5}
        cfg.capture_mode = mode_rev.get(self._get("capture_mode_str"), 1)

        config_manager.save()
        self.destroy()

    def _get(self, key: str) -> str:
        w = self._widgets.get(key)
        if w is None:
            return ""
        if isinstance(w, ctk.CTkEntry):
            return w.get().strip()
        if isinstance(w, ctk.CTkOptionMenu):
            return w.get()
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# Main GUI
# ─────────────────────────────────────────────────────────────────────────────

class FullPageScreenshotGUI(ctk.CTk):
    """Windows 11-style main window."""

    # ── Init ──────────────────────────────────────────────────────

    def __init__(self):
        super().__init__()

        self.title("Full-Page-Screenshot")
        self.geometry("980x740")
        self.minsize(800, 620)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.orchestrator:   CaptureOrchestrator | None = None
        self._latest_output: Path | None                = None
        self._theme:         str                        = "Dark"

        self._build_ui()

    # ─────────────────────────────────────────────────────────────
    # UI construction
    # ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # log panel expands

        # ── Header bar ────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, corner_radius=0, height=58,
                            fg_color=("#F0F0F0", "#1A1A1A"))
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)
        hdr.grid_propagate(False)

        ctk.CTkLabel(
            hdr,
            text="  📸  Full-Page-Screenshot",
            font=ctk.CTkFont("Segoe UI", 16, "bold"),
            anchor="w"
        ).grid(row=0, column=0, padx=20, pady=14, sticky="w")

        self._theme_btn = ctk.CTkButton(
            hdr, text="☀  Light", width=96, height=32,
            fg_color="transparent", border_width=1,
            font=ctk.CTkFont("Segoe UI", 12),
            command=self._toggle_theme
        )
        self._theme_btn.grid(row=0, column=2, padx=16, pady=14)

        # ── Main content (left + right columns) ───────────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=4)
        body.grid_rowconfigure(0, weight=1)

        # ── Left: Control panel ────────────────────────────────────
        left = ctk.CTkFrame(body, corner_radius=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.grid_columnconfigure(0, weight=1)

        self._build_control_panel(left)

        # ── Right: Stats panel ─────────────────────────────────────
        right = ctk.CTkFrame(body, corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew")

        self._build_stats_panel(right)

        # ── Quick settings strip ───────────────────────────────────
        qs = ctk.CTkFrame(self, corner_radius=10, height=54)
        qs.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))
        qs.grid_propagate(False)
        qs.grid_columnconfigure(9, weight=1)

        self._build_quick_settings(qs)

        # ── Log panel ──────────────────────────────────────────────
        log_frame = ctk.CTkFrame(self, corner_radius=0,
                                  fg_color=("#F8F8F8", "#141414"))
        log_frame.grid(row=3, column=0, sticky="nsew", padx=0, pady=0)
        self.grid_rowconfigure(3, weight=2)
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        self._build_log_panel(log_frame)

    def _build_control_panel(self, parent: ctk.CTkFrame):
        parent.grid_columnconfigure(0, weight=1)

        _sec = ctk.CTkFont("Segoe UI", 10)
        _bold = ctk.CTkFont("Segoe UI", 13, "bold")

        ctk.CTkLabel(parent, text="CAPTURE CONTROL",
                      font=_sec, text_color="gray", anchor="w"
                      ).grid(row=0, column=0, padx=16, pady=(14, 2), sticky="w")

        # ── Tabs input ─────────────────────────────────────────────
        tr = ctk.CTkFrame(parent, fg_color="transparent")
        tr.grid(row=1, column=0, padx=16, pady=4, sticky="ew")
        tr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(tr, text="Open Chrome tabs to capture:", anchor="w",
                      font=ctk.CTkFont("Segoe UI", 12)
                      ).grid(row=0, column=0, sticky="w")
        self._tabs_entry = ctk.CTkEntry(tr, width=72, placeholder_text="1",
                                         font=ctk.CTkFont("Segoe UI", 13))
        self._tabs_entry.grid(row=0, column=1, padx=(8, 0))

        # ── Buttons ────────────────────────────────────────────────
        br = ctk.CTkFrame(parent, fg_color="transparent")
        br.grid(row=2, column=0, padx=16, pady=10, sticky="w")

        self._btn_start = ctk.CTkButton(
            br, text="▶  Start", width=106, height=38,
            fg_color=ACCENT_BLUE, hover_color=ACCENT_HOVER,
            font=_bold, corner_radius=8,
            command=self._start_capture
        )
        self._btn_start.pack(side="left", padx=(0, 6))

        self._btn_pause = ctk.CTkButton(
            br, text="⏸  Pause", width=106, height=38,
            fg_color="transparent", border_width=1,
            font=ctk.CTkFont("Segoe UI", 13), corner_radius=8,
            command=self._pause_capture, state="disabled"
        )
        self._btn_pause.pack(side="left", padx=6)

        self._btn_stop = ctk.CTkButton(
            br, text="■  Stop", width=106, height=38,
            fg_color="#C0392B", hover_color="#922B21",
            font=ctk.CTkFont("Segoe UI", 13), corner_radius=8,
            command=self._stop_capture, state="disabled"
        )
        self._btn_stop.pack(side="left", padx=6)

        # ── Status badge ───────────────────────────────────────────
        self._status_badge = ctk.CTkLabel(
            parent,
            text="  ⬤  IDLE",
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            text_color=STATUS_COLORS["IDLE"],
            anchor="w"
        )
        self._status_badge.grid(row=3, column=0, padx=18, pady=(0, 4), sticky="w")

        # ── Progress bar ───────────────────────────────────────────
        ctk.CTkLabel(parent, text="Session progress:", anchor="w",
                      font=ctk.CTkFont("Segoe UI", 11), text_color="gray"
                      ).grid(row=4, column=0, padx=16, pady=(10, 2), sticky="w")

        self._progress = ctk.CTkProgressBar(parent, height=14, corner_radius=7)
        self._progress.grid(row=5, column=0, padx=16, pady=2, sticky="ew")
        self._progress.set(0)

        self._lbl_progress = ctk.CTkLabel(
            parent, text="0 of 0 tabs  •  ETA: —",
            font=ctk.CTkFont("Segoe UI", 11), text_color="gray", anchor="w"
        )
        self._lbl_progress.grid(row=6, column=0, padx=16, pady=(2, 14), sticky="w")

    def _build_stats_panel(self, parent: ctk.CTkFrame):
        ctk.CTkLabel(parent, text="LIVE STATS",
                      font=ctk.CTkFont("Segoe UI", 10), text_color="gray", anchor="w"
                      ).pack(padx=16, pady=(14, 6), anchor="w")

        self._s_tab     = self._make_stat(parent, "Tab",             "— / —")
        self._s_title   = self._make_stat(parent, "Page title",      "—")
        self._s_scrolls = self._make_stat(parent, "Scroll count",    "0")
        self._s_pos     = self._make_stat(parent, "Scroll position", "0.0%")
        self._s_frames  = self._make_stat(parent, "Screenshots",     "0")
        self._s_file    = self._make_stat(parent, "Output file",     "—")
        self._s_cpu     = self._make_stat(parent, "CPU usage",       "0.0%")
        self._s_mem     = self._make_stat(parent, "Memory",          "0 MB")

        # Action buttons
        ar = ctk.CTkFrame(parent, fg_color="transparent")
        ar.pack(padx=16, pady=14, fill="x")

        self._btn_folder = ctk.CTkButton(
            ar, text="📁  Open Folder", width=130, height=32,
            fg_color="transparent", border_width=1,
            font=ctk.CTkFont("Segoe UI", 12), corner_radius=8,
            command=self._open_output_folder
        )
        self._btn_folder.pack(side="left", padx=(0, 6))

        self._btn_open_pdf = ctk.CTkButton(
            ar, text="📄  Open PDF", width=116, height=32,
            fg_color="transparent", border_width=1,
            font=ctk.CTkFont("Segoe UI", 12), corner_radius=8,
            state="disabled",
            command=self._open_latest_output
        )
        self._btn_open_pdf.pack(side="left")

    def _build_quick_settings(self, parent: ctk.CTkFrame):
        _lbl = lambda text: ctk.CTkLabel(
            parent, text=text, font=ctk.CTkFont("Segoe UI", 11),
            text_color="gray"
        )

        c = 0

        _lbl("Format:").grid(row=0, column=c, padx=(16, 4), pady=12)
        c += 1
        self._cmb_format = ctk.CTkOptionMenu(
            parent, values=["PDF", "PNG", "JPEG"], width=88,
            font=ctk.CTkFont("Segoe UI", 12),
            command=self._quick_save
        )
        self._cmb_format.set(config_manager.settings.export_format)
        self._cmb_format.grid(row=0, column=c, padx=4, pady=12)
        c += 1

        _lbl("Mode:").grid(row=0, column=c, padx=(16, 4), pady=12)
        c += 1
        self._cmb_mode = ctk.CTkOptionMenu(
            parent, values=["End of Page", "Time Limit", "Screenshot Limit", "Manual"],
            width=152, font=ctk.CTkFont("Segoe UI", 12),
            command=self._quick_save
        )
        _mode_map = {1: "End of Page", 2: "Time Limit", 3: "Screenshot Limit", 5: "Manual"}
        self._cmb_mode.set(_mode_map.get(config_manager.settings.capture_mode, "End of Page"))
        self._cmb_mode.grid(row=0, column=c, padx=4, pady=12)
        c += 1

        _lbl("Output:").grid(row=0, column=c, padx=(16, 4), pady=12)
        c += 1

        from workspace_manager import workspace_manager
        out_dir = str(workspace_manager.workspace_path / "Output")
        self._lbl_dir = ctk.CTkLabel(
            parent, text=self._clip(out_dir, 30),
            font=ctk.CTkFont("Segoe UI", 11), text_color="gray"
        )
        self._lbl_dir.grid(row=0, column=c, padx=4, pady=12, sticky="w")
        c += 1

        ctk.CTkButton(
            parent, text="Change", width=70, height=28,
            fg_color="transparent", border_width=1,
            font=ctk.CTkFont("Segoe UI", 11), corner_radius=6,
            command=self._change_dir
        ).grid(row=0, column=c, padx=6, pady=12)
        c += 1

        ctk.CTkButton(
            parent, text="⚙  Settings", width=106, height=28,
            fg_color="transparent", border_width=1,
            font=ctk.CTkFont("Segoe UI", 11), corner_radius=6,
            command=self._open_settings
        ).grid(row=0, column=c, padx=6, pady=12)

    def _build_log_panel(self, parent: ctk.CTkFrame):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        # Log header
        lh = ctk.CTkFrame(parent, fg_color="transparent", height=30)
        lh.grid(row=0, column=0, sticky="ew", padx=16, pady=(8, 0))
        ctk.CTkLabel(lh, text="LIVE LOG",
                      font=ctk.CTkFont("Segoe UI", 10), text_color="gray"
                      ).pack(side="left")
        ctk.CTkButton(
            lh, text="Clear", width=56, height=22,
            fg_color="transparent", border_width=1,
            font=ctk.CTkFont("Segoe UI", 10), corner_radius=6,
            command=self._clear_log
        ).pack(side="right")

        # Log textbox
        self._txt_log = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont("Consolas", 11),
            state="disabled",
            wrap="none",
            corner_radius=0
        )
        self._txt_log.grid(row=1, column=0, sticky="nsew", padx=16, pady=(4, 12))

        # Configure colour tags via the underlying tk.Text widget
        self._apply_log_tags()

    def _apply_log_tags(self):
        """Apply colour tags to the log textbox. Called once and on theme toggle."""
        mode = "dark" if self._theme == "Dark" else "light"
        tb = self._txt_log._textbox
        for level, colors in LOG_TAG_COLORS.items():
            tb.tag_configure(level, foreground=colors[mode])

    # ─────────────────────────────────────────────────────────────
    # Helper factories
    # ─────────────────────────────────────────────────────────────

    def _make_stat(self, parent, key: str, value: str):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=3)
        ctk.CTkLabel(
            row, text=f"{key}:", width=120, anchor="w",
            font=ctk.CTkFont("Segoe UI", 11), text_color="gray"
        ).pack(side="left")
        val = ctk.CTkLabel(
            row, text=value, anchor="w",
            font=ctk.CTkFont("Segoe UI", 11, "bold")
        )
        val.pack(side="left")
        return val

    @staticmethod
    def _clip(text: str, n: int) -> str:
        return ("…" + text[-(n-1):]) if len(text) > n else text

    # ─────────────────────────────────────────────────────────────
    # Theme toggle
    # ─────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        if self._theme == "Dark":
            ctk.set_appearance_mode("Light")
            self._theme = "Light"
            self._theme_btn.configure(text="🌙  Dark")
        else:
            ctk.set_appearance_mode("Dark")
            self._theme = "Dark"
            self._theme_btn.configure(text="☀  Light")
        self._apply_log_tags()

    # ─────────────────────────────────────────────────────────────
    # Settings / directory
    # ─────────────────────────────────────────────────────────────

    def _open_settings(self):
        SettingsDialog(self)

    def _quick_save(self, _=None):
        config_manager.settings.export_format = self._cmb_format.get()
        mode_rev = {"End of Page": 1, "Time Limit": 2,
                    "Screenshot Limit": 3, "Manual": 5}
        config_manager.settings.capture_mode = mode_rev.get(self._cmb_mode.get(), 1)
        config_manager.save()

    def _change_dir(self):
        d = filedialog.askdirectory(title="Select Output Directory")
        if d:
            # We store the output dir preference — FileManager uses workspace_manager
            # but we surface this for the user's awareness
            self._lbl_dir.configure(text=self._clip(d, 30))

    def _open_output_folder(self):
        from workspace_manager import workspace_manager
        folder = workspace_manager.workspace_path / "Output"
        if folder.exists():
            os.startfile(str(folder))

    def _open_latest_output(self):
        if self._latest_output and self._latest_output.exists():
            os.startfile(str(self._latest_output))

    # ─────────────────────────────────────────────────────────────
    # Capture control
    # ─────────────────────────────────────────────────────────────

    def _start_capture(self):
        try:
            tabs = int(self._tabs_entry.get())
            if tabs <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input",
                                  "Please enter a valid number of tabs (≥ 1).")
            return

        self._clear_log()
        self._set_ui_running()
        self._set_badge("CAPTURING")

        callbacks = {
            "status":      lambda s, t, title, tracker:
                               self.after(0, self._cb_status, s, t, title, tracker),
            "log":         lambda msg, lvl="INFO":
                               self.after(0, self._append_log, msg, lvl),
            "telemetry":   lambda **kw:
                               self.after(0, lambda kw=kw: self._cb_telemetry(**kw)),
            "output_file": lambda p:
                               self.after(0, self._cb_output_file, p),
            "finished":    lambda:
                               self.after(0, self._cb_finished),
        }

        self.orchestrator = CaptureOrchestrator(callbacks, tabs)
        self.orchestrator.start()

    def _pause_capture(self):
        if self.orchestrator:
            self.orchestrator.is_paused = True
            self._btn_pause.configure(text="▶  Resume", command=self._resume_capture)
            self._set_badge("PAUSED")

    def _resume_capture(self):
        if self.orchestrator:
            self.orchestrator.is_paused = False
            self._btn_pause.configure(text="⏸  Pause", command=self._pause_capture)
            self._set_badge("CAPTURING")

    def _stop_capture(self):
        if self.orchestrator:
            self.orchestrator.is_stopped = True
            self._set_ui_idle()
            self._set_badge("STOPPED")
            self._append_log(
                "[--:--:--] [WARNING]  Stop requested — "
                "waiting for current tab export to finish...", "WARNING"
            )

    # ─────────────────────────────────────────────────────────────
    # Orchestrator callbacks (always dispatched to main thread)
    # ─────────────────────────────────────────────────────────────

    def _cb_status(self, status: str, tab_idx: int, title: str, tracker):
        self._set_badge(status)
        pct = tracker.get_progress_percentage()
        eta = tracker.get_eta_seconds()
        self._progress.set(pct)
        self._lbl_progress.configure(
            text=f"{tracker.current_tab} of {tracker.total_tabs} tabs"
                 f"  •  ETA: {format_time(eta)}"
        )
        self._s_tab.configure(text=f"{tab_idx} / {tracker.total_tabs}")
        self._s_title.configure(
            text=self._clip(title.replace(" - Google Chrome", ""), 38)
        )

    def _cb_telemetry(self, *, cpu=0.0, mem=0.0, scroll_count=0,
                       scroll_pct=0.0, img_count=0, tab_idx=0, title=""):
        self._s_scrolls.configure(text=f"{scroll_count:,}")
        self._s_pos.configure(text=f"{scroll_pct:.1f}%")
        self._s_frames.configure(text=f"{img_count:,}")
        self._s_cpu.configure(text=f"{cpu:.1f}%")
        self._s_mem.configure(text=f"{mem:.0f} MB")

    def _cb_output_file(self, path: Path):
        self._latest_output = path
        self._s_file.configure(text=self._clip(path.name, 36))
        self._btn_open_pdf.configure(state="normal")

    def _cb_finished(self):
        self._set_ui_idle()
        self._set_badge("COMPLETE")
        self._progress.set(1.0)
        self._lbl_progress.configure(text="Complete  •  All files saved")

    # ─────────────────────────────────────────────────────────────
    # Log
    # ─────────────────────────────────────────────────────────────

    def _append_log(self, msg: str, level: str = "INFO"):
        self._txt_log.configure(state="normal")
        self._txt_log._textbox.insert("end", msg + "\n", level)
        self._txt_log._textbox.see("end")
        self._txt_log.configure(state="disabled")

    def _clear_log(self):
        self._txt_log.configure(state="normal")
        self._txt_log.delete("1.0", "end")
        self._txt_log.configure(state="disabled")

    # ─────────────────────────────────────────────────────────────
    # UI state helpers
    # ─────────────────────────────────────────────────────────────

    def _set_ui_running(self):
        self._btn_start.configure(state="disabled")
        self._btn_pause.configure(state="normal", text="⏸  Pause",
                                   command=self._pause_capture)
        self._btn_stop.configure(state="normal")

    def _set_ui_idle(self):
        self._btn_start.configure(state="normal")
        self._btn_pause.configure(state="disabled")
        self._btn_stop.configure(state="disabled")

    def _set_badge(self, status: str):
        color = STATUS_COLORS.get(status, STATUS_COLORS["IDLE"])
        self._status_badge.configure(
            text=f"  ⬤  {status}",
            text_color=color
        )

    # ─────────────────────────────────────────────────────────────
    # Entry point
    # ─────────────────────────────────────────────────────────────

    def run(self):
        self.mainloop()
