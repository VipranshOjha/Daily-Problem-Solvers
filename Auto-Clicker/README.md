# 🏏 IPL Ticket Auto-Clicker

Frustrated by missing out on IPL tickets the moment they go live? This simple Python automation script helps you click the booking button **at the exact time tickets are released**, improving your chances of snagging those coveted seats before they sell out.

## 🚀 Features

- ⏰ Waits until a user-defined target time
- 🖱️ Automatically clicks at the specified screen coordinates
- 🧭 Useful for booking tickets or grabbing time-sensitive deals

## 🧠 How It Works

This script uses `pyautogui` to:
1. Wait until a specific time (e.g., when ticket sales go live)
2. Click at a specific coordinate on the screen (e.g., where the "Book Now" button appears)

## 🛠️ Requirements

- Python 3.x
- [pyautogui](https://pypi.org/project/pyautogui/)

Install the dependency:
```bash
pip install pyautogui
```

## 📄 Usage

1. Find the **X and Y coordinates** of the button you want to click (e.g., use a screen ruler or `pyautogui.position()` in an interactive session).
2. Update these coordinates and the desired click time in `main.py`:

```python
# Example values
x_coordinate = 500  
y_coordinate = 500  

target_hour = 22  # 10 PM
target_minute = 20
target_second = 0
```

3. Run the script before the ticket release time:

```bash
python main.py
```

The script will wait until your target time and then execute the click.

## ⚠️ Important Notes

- This script simulates mouse movements, so **do not move your mouse** or interrupt the automation while it's running.
- Make sure your system clock is accurate and synced.
- This doesn't bypass any queue or security measures—it's just a timed clicker.

## 📌 Disclaimer

This script is intended for **personal use** only and should be used responsibly. Do not use it to spam or violate terms of service of any ticketing website.

---
