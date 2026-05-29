"""
Privacy Window Switcher Application
Minimizes active windows or minimizes everything when an unrecognized face or shoulder-surfer is detected.
"""

import cv2
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import platform
import sys
from datetime import datetime
import json
import face_recognition
import pyautogui

class PrivacyFaceDetector:
    """Handles webcam access and logic to spot intruders or shoulder-surfers."""

    def __init__(self, known_face_path="my_face.jpg"):
        try:
            self.known_image = face_recognition.load_image_file(known_face_path)
            encodings = face_recognition.face_encodings(self.known_image)

            if len(encodings) == 0:
                raise Exception("No face found in the reference image! Please use a clear face photo.")

            self.known_encoding = encodings[0]
            self.cap = None
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load face image: {e}")
            raise

    def initialize_camera(self):
        """Initialize webcam connection."""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Cannot access webcam")

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            return True
        except Exception as e:
            print(f"Camera initialization error: {e}")
            return False

    def check_privacy_breach(self, strict_mode=False):
        """
        Returns (True, "reason") if a breach occurs, otherwise (False, "").
        Strict mode: Triggers if ANY face other than you is detected.
        Normal mode: Triggers if more than 1 face is in frame (someone looking over your shoulder).
        """
        if not self.cap or not self.cap.isOpened():
            return False, "Camera Offline"

        ret, frame = self.cap.read()
        if not ret:
            return False, "Failed to read frame"

        # Convert to RGB for face_recognition library
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if len(face_locations) == 0:
            return False, "" # No faces at all

        # If more than one person is looking at the screen
        if len(face_locations) > 1:
            return True, f"Multiple Faces Detected ({len(face_locations)})"

        # If exactly 1 face is present, check if it's actually YOU in strict mode
        if strict_mode and len(face_locations) == 1:
            encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            if encodings:
                matches = face_recognition.compare_faces([self.known_encoding], encodings[0])
                face_dis = face_recognition.face_distance([self.known_encoding], encodings[0])
                if not matches[0] or face_dis[0] >= 0.6:
                    return True, "Unknown Face Detected"

        return False, ""

    def release_camera(self):
        """Release webcam resources."""
        if self.cap:
            self.cap.release()
            self.cap = None


class WindowSwitcher:
    """Handles triggering safety macros to hide sensitive content."""

    @staticmethod
    def trigger_privacy_action(action_type="Minimize All"):
        """Executes a hotkey macro based on the user setting."""
        system = platform.system().lower()
        
        try:
            if action_type == "Minimize All":
                if system == "windows":
                    pyautogui.hotkey('win', 'd')
                elif system == "darwin":  # macOS
                    pyautogui.hotkey('command', 'f3')  # Show Desktop
                else:  # Linux
                    pyautogui.hotkey('win', 'd')
                    
            elif action_type == "Switch Window (Alt+Tab)":
                if system == "darwin":
                    pyautogui.hotkey('command', 'tab')
                else:
                    pyautogui.hotkey('alt', 'tab')

            elif action_type == "Switch Virtual Desktop":
                if system == "windows":
                    # Moves one desktop to the right
                    pyautogui.hotkey('win', 'ctrl', 'right')
                elif system == "darwin":  # macOS
                    # Moves one space to the right (Control + Right Arrow)
                    pyautogui.hotkey('ctrl', 'right')
                else:  # Linux (Standard GNOME/KDE shortcuts)
                    # Often Ctrl + Alt + Right Arrow or Super + PageDown
                    pyautogui.hotkey('ctrl', 'alt', 'right')

            return True
        except Exception as e:
            print(f"Action trigger error: {e}")
            return False


class PrivacySwitcherApp:
    """Main application GUI matching the UI philosophy of Auto-Screen-Lock."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Privacy Window Switcher")
        self.root.geometry("500x440")
        self.root.minsize(400, 380)

        # Application state
        self.is_monitoring = False
        self.detector = PrivacyFaceDetector("my_face.jpg") # Make sure this file exists
        self.switcher = WindowSwitcher()
        self.monitoring_thread = None
        self.cooldown_until = 0

        # Configuration defaults
        self.strict_mode = tk.BooleanVar(value=True)
        self.action_type = tk.StringVar(value="Minimize All")

        self.setup_ui()
        self.update_status()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(main_frame, text="Privacy Window Switcher", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Status Panel
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.status_label = ttk.Label(status_frame, text="Stopped", foreground="red", font=("Arial", 11, "bold"))
        self.status_label.grid(row=0, column=0, sticky=tk.W)

        self.incident_label = ttk.Label(status_frame, text="Environment: Clear", foreground="green")
        self.incident_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # Controls Panel
        controls_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        controls_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.start_button = ttk.Button(controls_frame, text="Start Shielding", command=self.toggle_monitoring)
        self.start_button.grid(row=0, column=0, padx=(0, 10))

        ttk.Button(controls_frame, text="Test Action Macro", command=self.test_action).grid(row=0, column=1)

        # Settings Panel
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        strict_check = ttk.Checkbutton(
            settings_frame, 
            text="Strict Mode (Trigger if anyone else sits at my desk alone)", 
            variable=self.strict_mode
        )
        strict_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        ttk.Label(settings_frame, text="Action Target:").grid(row=1, column=0, sticky=tk.W)
        action_dropdown = ttk.Combobox(settings_frame, textvariable=self.action_type, state="readonly")
        
        # Added "Switch Virtual Desktop" to the values tuple
        action_dropdown['values'] = ("Minimize All", "Switch Window (Alt+Tab)", "Switch Virtual Desktop")
        
        action_dropdown.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))

        # Log Panel
        log_frame = ttk.LabelFrame(main_frame, text="Privacy Events Log", padding="10")
        log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, height=6, width=50)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def test_action(self):
        result = messagebox.askyesno("Test Macro", "This will fire your choice of hotkey sequence in 2 seconds. Ready?")
        if result:
            self.root.after(2000, lambda: self.switcher.trigger_privacy_action(self.action_type.get()))

    def toggle_monitoring(self):
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def start_monitoring(self):
        if not self.detector.initialize_camera():
            messagebox.showerror("Error", "Cannot access webcam.")
            return

        self.is_monitoring = True
        self.start_button.config(text="Stop Shielding")
        self.log_message("Privacy Shield Activated")

        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()

    def stop_monitoring(self):
        self.is_monitoring = False
        self.start_button.config(text="Start Shielding")
        self.detector.release_camera()
        self.log_message("Privacy Shield Deactivated")

    def monitoring_loop(self):
        while self.is_monitoring:
            try:
                # Avoid multi-firing the switch macro repeatedly during an incident loop
                if time.time() < self.cooldown_until:
                    time.sleep(0.5)
                    continue

                breach, reason = self.detector.check_privacy_breach(strict_mode=self.strict_mode.get())

                if breach:
                    self.log_message(f"ALERT: {reason}! Triggering safe action...")
                    self.switcher.trigger_privacy_action(self.action_type.get())
                    # Prevent macro spamming for 5 seconds after a switch occurs
                    self.cooldown_until = time.time() + 5.0 

                time.sleep(0.3)
            except Exception as e:
                print(f"Monitoring exception: {e}")
                time.sleep(1)

    def update_status(self):
        if self.is_monitoring:
            self.status_label.config(text="SHIELD ACTIVE", foreground="green")
            if time.time() < self.cooldown_until:
                self.incident_label.config(text="Status: Post-Breach Cooldown Window...", foreground="orange")
            else:
                self.incident_label.config(text="Status: Scanning environment safely", foreground="green")
        else:
            self.status_label.config(text="Shield Stopped", foreground="red")
            self.incident_label.config(text="Status: Unprotected", foreground="gray")

        self.root.after(200, self.update_status)

    def on_closing(self):
        if self.is_monitoring:
            self.stop_monitoring()
        self.root.destroy()

if __name__ == "__main__":
    app = PrivacySwitcherApp()
    app.root.mainloop()