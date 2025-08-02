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


class FaceDetector:
    """Handles webcam access and face detection using OpenCV."""
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.cap = None
        self.is_running = False
        
    def initialize_camera(self):
        """Initialize webcam connection."""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Cannot access webcam")
            
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 10)  # Lower FPS to reduce CPU usage
            return True
        except Exception as e:
            print(f"Camera initialization error: {e}")
            return False
    
    def detect_face(self):
        """Detect if a face is present in the current frame."""
        if not self.cap or not self.cap.isOpened():
            return False
            
        ret, frame = self.cap.read()
        if not ret:
            return False
            
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        return len(faces) > 0
    
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
                subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
            elif system == "linux":
                # Try different Linux screen lockers
                lock_commands = [
                    "gnome-screensaver-command -l",
                    "xdg-screensaver lock",
                    "dm-tool lock",
                    "loginctl lock-session"
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
        self.root.minsize(400, 350)  # Minimum size to prevent UI breaking
        
        # Application state
        self.is_monitoring = False
        self.face_detector = FaceDetector()
        self.screen_locker = ScreenLocker()
        self.monitoring_thread = None
        self.last_face_time = time.time()
        
        # Configuration
        self.config = self.load_config()
        self.timeout_seconds = self.config.get('timeout_seconds', 30)
        self.warning_enabled = self.config.get('warning_enabled', True)
        self.warning_seconds = self.config.get('warning_seconds', 5)
        
        self.setup_ui()
        self.update_status()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_config(self):
        """Load configuration from file."""
        try:
            with open('screen_lock_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_config(self):
        """Save configuration to file."""
        config = {
            'timeout_seconds': self.timeout_seconds,
            'warning_enabled': self.warning_enabled,
            'warning_seconds': self.warning_seconds
        }
        with open('screen_lock_config.json', 'w') as f:
            json.dump(config, f, indent=2)
    
    def setup_ui(self):
        """Create the user interface."""
        # Configure main window grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)  # Log section expands
        
        # Title
        title_label = ttk.Label(main_frame, text="Automatic Screen Lock", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Stopped", foreground="red")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.face_status_label = ttk.Label(status_frame, text="Face: Not detected")
        self.face_status_label.grid(row=1, column=0, sticky=tk.W)
        
        self.timer_label = ttk.Label(status_frame, text="Timer: --")
        self.timer_label.grid(row=2, column=0, sticky=tk.W)
        
        # Controls section
        controls_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        controls_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_button = ttk.Button(controls_frame, text="Start Monitoring", command=self.toggle_monitoring)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Test Camera", command=self.test_camera).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(controls_frame, text="Test Lock", command=self.test_lock).grid(row=0, column=2)
        
        # Settings section
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Timeout setting
        ttk.Label(settings_frame, text="Lock timeout (seconds):").grid(row=0, column=0, sticky=tk.W)
        self.timeout_var = tk.StringVar(value=str(self.timeout_seconds))
        timeout_entry = ttk.Entry(settings_frame, textvariable=self.timeout_var, width=10)
        timeout_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        timeout_entry.bind('<FocusOut>', self.update_timeout)
        
        # Warning setting
        self.warning_var = tk.BooleanVar(value=self.warning_enabled)
        warning_check = ttk.Checkbutton(settings_frame, text="Enable warning before lock", 
                                      variable=self.warning_var, command=self.update_warning)
        warning_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Configure log frame for resizing
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, width=50)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        # (Grid weights now configured at the beginning of setup_ui)
    
    def log_message(self, message):
        """Add a message to the activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Keep only last 100 lines
        lines = self.log_text.get("1.0", tk.END).split("\n")
        if len(lines) > 100:
            self.log_text.delete("1.0", f"{len(lines)-100}.0")
    
    def update_timeout(self, event=None):
        """Update timeout setting."""
        try:
            self.timeout_seconds = max(5, int(self.timeout_var.get()))
            self.timeout_var.set(str(self.timeout_seconds))
            self.save_config()
        except ValueError:
            self.timeout_var.set(str(self.timeout_seconds))
    
    def update_warning(self):
        """Update warning setting."""
        self.warning_enabled = self.warning_var.get()
        self.save_config()
    
    def test_camera(self):
        """Test camera functionality."""
        if self.face_detector.initialize_camera():
            face_detected = self.face_detector.detect_face()
            self.face_detector.release_camera()
            
            if face_detected:
                messagebox.showinfo("Camera Test", "Camera working! Face detected.")
                self.log_message("Camera test successful - face detected")
            else:
                messagebox.showwarning("Camera Test", "Camera working, but no face detected. Make sure you're visible to the camera.")
                self.log_message("Camera test successful - no face detected")
        else:
            messagebox.showerror("Camera Test", "Camera test failed! Please check your webcam connection.")
            self.log_message("Camera test failed")
    
    def test_lock(self):
        """Test screen lock functionality."""
        result = messagebox.askyesno("Test Lock", "This will lock your screen immediately. Continue?")
        if result:
            self.log_message("Testing screen lock")
            if self.screen_locker.lock_screen():
                self.log_message("Screen lock test successful")
            else:
                self.log_message("Screen lock test failed")
                messagebox.showerror("Test Lock", "Screen lock test failed!")
    
    def toggle_monitoring(self):
        """Start or stop monitoring."""
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def start_monitoring(self):
        """Start face detection monitoring."""
        if not self.face_detector.initialize_camera():
            messagebox.showerror("Error", "Cannot access webcam. Please check your camera connection.")
            return
        
        self.is_monitoring = True
        self.last_face_time = time.time()
        self.start_button.config(text="Stop Monitoring")
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.log_message("Monitoring started")
    
    def stop_monitoring(self):
        """Stop face detection monitoring."""
        self.is_monitoring = False
        self.start_button.config(text="Start Monitoring")
        self.face_detector.release_camera()
        self.log_message("Monitoring stopped")
    
    def monitoring_loop(self):
        """Main monitoring loop running in separate thread."""
        while self.is_monitoring:
            try:
                face_detected = self.face_detector.detect_face()
                
                if face_detected:
                    self.last_face_time = time.time()
                
                # Check if we should lock the screen
                time_since_face = time.time() - self.last_face_time
                
                if time_since_face >= self.timeout_seconds:
                    self.log_message("No face detected for timeout period - locking screen")
                    if self.screen_locker.lock_screen():
                        self.log_message("Screen locked successfully")
                    else:
                        self.log_message("Failed to lock screen")
                    
                    # Reset timer after locking
                    self.last_face_time = time.time()
                
                elif (self.warning_enabled and 
                      time_since_face >= (self.timeout_seconds - self.warning_seconds)):
                    # Show warning (could add system notification here)
                    pass
                
                time.sleep(0.5)  # Check every 500ms
                
            except Exception as e:
                self.log_message(f"Monitoring error: {e}")
                time.sleep(1)
    
    def update_status(self):
        """Update status display."""
        if self.is_monitoring:
            self.status_label.config(text="Monitoring", foreground="green")
            
            # Update face status
            if hasattr(self, 'last_face_time'):
                time_since_face = time.time() - self.last_face_time
                if time_since_face < 1:
                    self.face_status_label.config(text="Face: Detected", foreground="green")
                else:
                    self.face_status_label.config(text="Face: Not detected", foreground="red")
                
                # Update timer
                remaining = max(0, self.timeout_seconds - time_since_face)
                self.timer_label.config(text=f"Timer: {remaining:.1f}s")
            else:
                self.face_status_label.config(text="Face: Initializing...")
                self.timer_label.config(text="Timer: --")
        else:
            self.status_label.config(text="Stopped", foreground="red")
            self.face_status_label.config(text="Face: Not monitoring", foreground="gray")
            self.timer_label.config(text="Timer: --")
        
        # Schedule next update
        self.root.after(100, self.update_status)
    
    def on_closing(self):
        """Handle application closing."""
        if self.is_monitoring:
            self.stop_monitoring()
        self.root.destroy()
    
    def run(self):
        """Start the application."""
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