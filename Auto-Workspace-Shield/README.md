# 🛡️ Auto Workspace Shield

Working with sensitive information in public spaces or shared offices? Auto Workspace Shield helps protect your privacy by automatically hiding your screen whenever someone else appears in view of your webcam.

Using real-time face detection, the application monitors your workspace and triggers a safety action whenever it detects a potential shoulder-surfer or an unauthorized person looking at your screen.

## 🚀 Features

* 👤 Recognizes the authorized user using facial recognition
* 👥 Detects multiple faces in the webcam feed
* 🚨 Automatically triggers privacy protection when a potential shoulder-surfer is detected
* 🖥️ Supports multiple privacy actions:

  * Minimize all windows
  * Switch to another window
  * Switch to a different virtual desktop
* 🔒 Optional Strict Mode for detecting unknown users even when only one face is present
* 📋 Built-in event log for monitoring privacy incidents

## 🧠 How It Works

The application uses your webcam and facial recognition to continuously monitor who is in front of your computer.

### Normal Mode

If more than one face is detected in the frame, the application assumes someone may be looking over your shoulder and activates the configured privacy action.

### Strict Mode

If a face other than the registered user is detected, the application immediately activates the privacy action—even if only one person is present.

## 🛠️ Requirements

* Python 3.x
* Webcam
* A reference image named `my_face.jpg`

### Dependencies

```bash
pip install opencv-python face-recognition pyautogui
```

## 📄 Usage

### 1. Add Your Reference Photo

Place a clear image of your face in the project directory and name it:

```text
my_face.jpg
```

### 2. Run the Application

```bash
python main.py
```

### 3. Configure Protection Settings

Choose:

* Privacy action to trigger
* Whether to enable Strict Mode

Available actions:

* Minimize All Windows
* Switch Window (Alt + Tab)
* Switch Virtual Desktop

### 4. Start Shielding

Click **Start Shielding** and the application will begin monitoring your workspace.

Whenever a privacy breach is detected, the selected action will be triggered automatically.

## ⚠️ Important Notes

* Use a clear, well-lit reference image for reliable face recognition.
* Webcam access must remain enabled while monitoring.
* Sudden lighting changes may affect detection accuracy.
* A cooldown period is applied after each trigger to prevent repeated activations.
* The application performs all processing locally on your device.

## 📌 Example Use Cases

* Working in a library
* Coding in a shared office
* Viewing confidential documents
* Demonstrating projects in public spaces
* Protecting personal information from shoulder-surfers

## 📌 Disclaimer

This project is intended for educational and personal productivity purposes. Face recognition accuracy may vary depending on camera quality, lighting conditions, and viewing angles. Always verify that your privacy protection settings behave as expected before relying on them in sensitive environments.

---

Built with Python, OpenCV, Face Recognition, and a healthy dose of workplace paranoia.
