# 👀 Auto Screen Lock

Do you **forget to lock your computer** when you walk away for a snack, a call, or just because life happens?

**Auto Screen Lock** makes sure your files, chats, and secrets stay safe—by locking your screen automatically when you’re not around.

---

## 🚩 What is this?

Auto Screen Lock is a Python application with a simple **GUI** that uses your webcam and **face recognition** to check if you’re still at your desk.
If you leave, it gives you a short grace period, then **locks your screen** using the system’s native lock.

---

## 🪄 Features

✅ **Face Recognition Based:** Uses your stored reference photo to verify it’s *you*.
✅ **Cross-Platform Support:** Works on **Windows, macOS, and Linux** with OS-level lock commands.
✅ **Custom Timeout:** Choose how long the system waits before locking (default: `30s`).
✅ **Warning Mode:** Enable an optional last warning before the lock triggers.
✅ **GUI Controls:** Start/stop monitoring, adjust settings, run test camera/lock functions.
✅ **Activity Log:** Built-in log window tracks events (face detected, lock triggered, etc.).
✅ **Persistent Config:** Settings are saved to `screen_lock_config.json` and restored automatically.

---

## ⚙️ Installation & Setup

1. **Clone the repo:**

   ```bash
   git clone https://github.com/VipranshOjha/Daily-Problem-Solvers.git
   cd Daily-Problem-Solvers/Auto-Screen-Lock
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   Dependencies include:

   * `opencv-python`
   * `face_recognition`
   * `tkinter` (usually pre-installed with Python)
   * `dlib` (needed by `face_recognition`)

3. **Provide your face reference image:**
   Place a clear photo of yourself as `my_face.jpg` (or change the path in `main.py`).

4. **Run the app:**

   ```bash
   python main.py
   ```

---

## ⚙️ How it works

* Continuously captures webcam frames.
* Compares detected faces with your saved reference image.
* **If your face is missing** for more than the timeout → screen locks.
* Face returns before timeout? Timer resets, you’re safe.
* All actions are logged in the app for transparency.

---

## 🛠 Supported Platforms

| OS      | Lock Command(s) Tried                                                                           |
| ------- | ----------------------------------------------------------------------------------------------- |
| Windows | `rundll32.exe user32.dll,LockWorkStation`                                                       |
| macOS   | `CGSession -suspend`                                                                            |
| Linux   | `gnome-screensaver-command -l`, `xdg-screensaver lock`, `dm-tool lock`, `loginctl lock-session` |

---

## ⚙️ Configuration

Settings are saved in `screen_lock_config.json`:

```json
{
  "timeout_seconds": 10,
  "warning_enabled": true,
  "warning_seconds": 5
}
```

* `timeout_seconds`: How long (in seconds) before locking.
* `warning_enabled`: Whether a warning countdown should be shown.
* `warning_seconds`: How many seconds before the lock the warning appears.

---

## 📝 Why I built this

Because I kept leaving my screen unlocked 😅 and returned to… “pranks” on Slack or worse, exposed docs.
This app fixes it—quietly, automatically, and cross-platform.

---

## 📬 Feedback / Contribute

Want to improve it? Found a bug?
Open an **issue** or **PR** in this repo. Contributions welcome!

---

🔒 **Protect your work, even when you forget.**
Run this app and stop worrying about unlocked screens forever.
