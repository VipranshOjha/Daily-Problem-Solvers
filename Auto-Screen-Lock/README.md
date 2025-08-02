# 👀 Auto Screen Lock

Do you **keep forgetting to lock your computer** when you walk away for a quick snack, call, or just because life happens?  
Auto Screen Lock’s got your back—so your files, notes and secrets aren’t left open for anyone nearby!

## 🚩 What is this?

Auto Screen Lock is a tiny script that uses your webcam to watch whether you’re actually *there* at your computer.  
If you leave, it gives you a few seconds—then **locks the screen** for you. Magic, no extra clicks and no more “oops, forgot to lock!” moments.

## 🪄 Features (tiny but mighty)

- **Completely Automatic:** Looks for your face, locks if you’re gone. That simple.
- **Decide Your Timeout:** You set how long your computer waits before locking (default: 30 seconds).
- **Works on Most Setups:** Mac, Windows, Linux (just need Python & OpenCV!)
- **Resource-Light:** Won’t slow your laptop down. Sits quietly until you ditch your seat.
- **Fail-safe Mode:** (Optional) Gives you a short beep/grace period as a “last warning.”

## 💾 Setup (you’ll finish before your coffee cools)

1. **Clone or Download:**
    ```bash
    git clone https://github.com/VipranshOjha/Daily-Problem-Solvers.git
    cd Daily-Problem-Solvers/Auto-Screen-Lock
    ```
2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3. **Run it:**
    ```bash
    python main.py
    ```

- Change how many seconds before locking (`TIMEOUT`) in the code (or in the GUI if you added it).

## ⚙️ How does it work?

- “Sees” you with your webcam.
- **If your face disappears:** Starts counting seconds.
- If you don’t return on time: **Locks your screen** (uses the OS’s normal lock for security).
- Sit down again: Detects you, timer resets, and you’re good!

## 🛠 Supported Platforms

| OS        | Lock Command Example                                    |
|-----------|--------------------------------------------------------|
| Windows   | `rundll32.exe user32.dll,LockWorkStation`              |
| Mac       | `osascript -e 'tell application "System Events" to keystroke "q" using {control down, command down}'`or CGSession |
| Linux     | `gnome-screensaver-command -l` (or `xdg-screensaver lock`) |

## 📝 Why did I build this?

Because *I* kept leaving screens unlocked and came back to embarrassing Slack messages or, worse, open docs.  
No more. Works quietly, so I don’t have to remember.

## ❓ Feedback / Want tweaks?

Open an issue, PR or just yell at me in the repo. Happy to see if anyone else wants to make this better.

**Protect your stuff, even when you forget.**  
Add this to your daily workflow and never worry about unlocked screens again.
