# Typing Speed Tracker ⌨️

A desktop typing speed test application built using **Python** and **Tkinter**.  
This tool measures **typing speed (WPM)**, **accuracy**, and **consistency**, while providing real-time visual feedback and a live performance graph.

---

## 🧠 Why I Built This

While coding regularly, I realized that typing is one of the most fundamental skills for a developer — yet it’s often ignored.  
Most online typing tools are either cluttered with ads, require an internet connection, or provide limited insights beyond basic WPM.

I built this project to:

- Improve and **track my own typing speed and accuracy**
- Practice building a **real-time, event-driven GUI application**
- Work with **state management, timers, and visual feedback** in Python
- Create a tool that I would actually use during my daily routine

This project is both a **personal productivity tool** and a **problem-solving exercise**.

---

## 🚀 Features

### ⏱️ Multiple Test Modes
- 30-second timed test
- 60-second timed test
- 25-word challenge mode

### 🧠 Real-Time Feedback
- Live WPM calculation
- Accuracy percentage updates as you type
- Strict Mode:
  - Mistakes are permanently marked once made

### 🎨 Visual Typing Feedback
- 🟢 Correct characters
- 🔴 Incorrect characters
- ⚪ Pending characters

### 📈 Live Performance Graph
- Dynamic WPM graph updated every second
- Helps visualize typing consistency during the test

### 🌙 UI Customization
- Dark / Light theme toggle
- Clean, distraction-free interface
- Monospaced font for accurate typing experience

---

## 🖥️ Tech Stack

- **Python 3**
- **Tkinter** (GUI framework)
- Standard libraries:
  - `time`
  - `random`

No external dependencies required.

---

## 🧩 How It Works

1. A random sentence is selected from a predefined dataset.
2. The test starts automatically when typing begins.
3. Each keystroke:
   - Updates WPM and accuracy
   - Highlights characters based on correctness
4. WPM data is recorded every second and plotted on a graph.
5. The test ends automatically based on the selected mode.

---

## ▶️ How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/VipranshOjha/Daily-Problem-Solvers.git
