"""
Automatic Screen Lock Application
Locks computer screen when user's face is not detected for a specified period.
"""

import cv2
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import os
import platform
import sys
from datetime import datetime
import json
import subprocess
import face_recognition


class FaceRecognizer:
    """Handles webcam access and face recognition using face_recognition library."""

    def __init__(self, known_face_path="my_face.jpg"):  # Change this to your photo
        try:
            self.known_image = face_recognition.load_image_file(known_face_path)
            encodings = face_recognition.face_encodings(self.known_image)

            if len(encodings) == 0:
                raise Exception("No face found in the reference image! Please use a clear face photo.")

            self.known_encoding = encodings[0]
            self.cap = None
            self.is_running = False
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load face image: {e}")
            raise

    def initialize_camera(self):
        """Initialize webcam connection."""
        try:
            self.cap = cv2.VideoCapture(0)  # Use 0 for default camera
            if not self.cap.isOpened():
                raise Exception("Cannot access webcam")

            # Camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 10)
            return True
        except Exception as e:
            print(f"Camera initialization error: {e}")
            return False

    def detect_face(self):
        """Return True if the known face is recognized in the current frame."""
        if not self.cap or not self.cap.isOpened():
            return False

        ret, frame = self.cap.read()
        if not ret:
            return False

        # Convert to RGB (face_recognition expects RGB images)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_frame)

        for encodeFace in encodings:
            matches = face_recognition.compare_faces([self.known_encoding], encodeFace)
            faceDis = face_recognition.face_distance([self.known_encoding], encodeFace)
            if matches[0] and faceDis[0] < 0.6:  # threshold
                return True

        return False

    def release_camera(self):
        """Release webcam resources."""
        if self.cap:
            self.cap.release()
            self.cap = None


class ScreenLocker:
    """Handles screen locking for different operating systems."""

    @staticmethod
    def lock_screen():
        """Lock the screen based on the operating system."""
        system = platform.system().lower()

        try:
            if system == "windows":
                os.system("rundll32.exe user32.dll,LockWorkStation")
            elif system == "darwin":  # macOS
                subprocess.run(
                    ["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"]
                )
            elif system == "linux":
                # Try different Linux screen lockers
                lock_commands = [
                    "gnome-screensaver-command -l",
                    "xdg-screensaver lock",
                    "dm-tool lock",
                    "loginctl lock-session",
                ]

                for cmd in lock_commands:
                    try:
                        subprocess.run(cmd.split(), check=True)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                else:
                    raise Exception("No suitable screen locker found")
            else:
                raise Exception(f"Unsupported operating system: {system}")

            return True
        except Exception as e:
            print(f"Screen lock error: {e}")
            return False


class AutoScreenLockApp:
    """Main application class with GUI interface."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Automatic Screen Lock")
        self.root.geometry("500x400")
        self.root.minsize(400, 350)

        # Application state
        self.is_monitoring = False
        self.face_detector = FaceRecognizer(r"D:\python\github\photo.jpg")  # photo
        self.screen_locker = ScreenLocker()
        self.monitoring_thread = None
        self.last_face_time = time.time()

        # Configuration
        self.config = self.load_config()
        self.timeout_seconds = self.config.get("timeout_seconds", 30)
        self.warning_enabled = self.config.get("warning_enabled", True)
        self.warning_seconds = self.config.get("warning_seconds", 5)

        self.setup_ui()
        self.update_status()

        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_config(self):
        """Load configuration from file."""
        try:
            with open("screen_lock_config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_config(self):
        """Save configuration to file."""
        config = {
            "timeout_seconds": self.timeout_seconds,
            "warning_enabled": self.warning_enabled,
            "warning_seconds": self.warning_seconds,
        }
        with open("screen_lock_config.json", "w") as f:
            json.dump(config, f, indent=2)

    def setup_ui(self):
        """Create the user interface."""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)

        title_label = ttk.Label(main_frame, text="Automatic Screen Lock", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.status_label = ttk.Label(status_frame, text="Stopped", foreground="red")
        self.status_label.grid(row=0, column=0, sticky=tk.W)

        self.face_status_label = ttk.Label(status_frame, text="Face: Not detected")
        self.face_status_label.grid(row=1, column=0, sticky=tk.W)

        self.timer_label = ttk.Label(status_frame, text="Timer: --")
        self.timer_label.grid(row=2, column=0, sticky=tk.W)

        controls_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        controls_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.start_button = ttk.Button(controls_frame, text="Start Monitoring", command=self.toggle_monitoring)
        self.start_button.grid(row=0, column=0, padx=(0, 10))

        ttk.Button(controls_frame, text="Test Camera", command=self.test_camera).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(controls_frame, text="Test Lock", command=self.test_lock).grid(row=0, column=2)

        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(settings_frame, text="Lock timeout (seconds):").grid(row=0, column=0, sticky=tk.W)
        self.timeout_var = tk.StringVar(value=str(self.timeout_seconds))
        timeout_entry = ttk.Entry(settings_frame, textvariable=self.timeout_var, width=10)
        timeout_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        timeout_entry.bind("<FocusOut>", self.update_timeout)

        self.warning_var = tk.BooleanVar(value=self.warning_enabled)
        warning_check = ttk.Checkbutton(
            settings_frame, text="Enable warning before lock", variable=self.warning_var, command=self.update_warning
        )
        warning_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, height=8, width=50)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)

        lines = self.log_text.get("1.0", tk.END).split("\n")
        if len(lines) > 100:
            self.log_text.delete("1.0", f"{len(lines)-100}.0")

    def update_timeout(self, event=None):
        try:
            self.timeout_seconds = max(5, int(self.timeout_var.get()))
            self.timeout_var.set(str(self.timeout_seconds))
            self.save_config()
        except ValueError:
            self.timeout_var.set(str(self.timeout_seconds))

    def update_warning(self):
        self.warning_enabled = self.warning_var.get()
        self.save_config()

    def test_camera(self):
        if self.face_detector.initialize_camera():
            face_detected = self.face_detector.detect_face()
            self.face_detector.release_camera()

            if face_detected:
                messagebox.showinfo("Camera Test", "Camera working! Face detected.")
                self.log_message("Camera test successful - face detected")
            else:
                messagebox.showwarning(
                    "Camera Test", "Camera working, but no face detected. Make sure you're visible to the camera."
                )
                self.log_message("Camera test successful - no face detected")
        else:
            messagebox.showerror("Camera Test", "Camera test failed! Please check your webcam connection.")
            self.log_message("Camera test failed")

    def test_lock(self):
        result = messagebox.askyesno("Test Lock", "This will lock your screen immediately. Continue?")
        if result:
            self.log_message("Testing screen lock")
            if self.screen_locker.lock_screen():
                self.log_message("Screen lock test successful")
            else:
                self.log_message("Screen lock test failed")
                messagebox.showerror("Test Lock", "Screen lock test failed!")

    def toggle_monitoring(self):
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def start_monitoring(self):
        if not self.face_detector.initialize_camera():
            messagebox.showerror("Error", "Cannot access webcam. Please check your camera connection.")
            return

        self.is_monitoring = True
        self.last_face_time = time.time()
        self.start_button.config(text="Stop Monitoring")

        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()

        self.log_message("Monitoring started")

    def stop_monitoring(self):
        self.is_monitoring = False
        self.start_button.config(text="Start Monitoring")
        self.face_detector.release_camera()
        self.log_message("Monitoring stopped")

    def monitoring_loop(self):
        while self.is_monitoring:
            try:
                face_detected = self.face_detector.detect_face()

                if face_detected:
                    self.last_face_time = time.time()

                time_since_face = time.time() - self.last_face_time

                if time_since_face >= self.timeout_seconds:
                    self.log_message("No face detected for timeout period - locking screen")
                    if self.screen_locker.lock_screen():
                        self.log_message("Screen locked successfully")
                    else:
                        self.log_message("Failed to lock screen")

                    self.last_face_time = time.time()

                elif self.warning_enabled and time_since_face >= (self.timeout_seconds - self.warning_seconds):
                    pass

                time.sleep(0.5)

            except Exception as e:
                self.log_message(f"Monitoring error: {e}")
                time.sleep(1)

    def update_status(self):
        if self.is_monitoring:
            self.status_label.config(text="Monitoring", foreground="green")

            if hasattr(self, "last_face_time"):
                time_since_face = time.time() - self.last_face_time
                if time_since_face < 1:
                    self.face_status_label.config(text="Face: Detected", foreground="green")
                else:
                    self.face_status_label.config(text="Face: Not detected", foreground="red")

                remaining = max(0, self.timeout_seconds - time_since_face)
                self.timer_label.config(text=f"Timer: {remaining:.1f}s")
            else:
                self.face_status_label.config(text="Face: Initializing...")
                self.timer_label.config(text="Timer: --")
        else:
            self.status_label.config(text="Stopped", foreground="red")
            self.face_status_label.config(text="Face: Not monitoring", foreground="gray")
            self.timer_label.config(text="Timer: --")

        self.root.after(100, self.update_status)

    def on_closing(self):
        if self.is_monitoring:
            self.stop_monitoring()
        self.root.destroy()

    def run(self):
        self.log_message("Application started")
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = AutoScreenLockApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)
