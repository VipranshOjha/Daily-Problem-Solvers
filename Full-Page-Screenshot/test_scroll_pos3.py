import pyautogui
import pyperclip
import time
import pygetwindow as gw
import subprocess
import os

def test():
    # Attempt to find Chrome, or launch it if not found
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if os.path.exists(chrome_path):
        subprocess.Popen([chrome_path, "https://en.wikipedia.org/wiki/Main_Page"])
        time.sleep(3)
    
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.1)
    pyautogui.write("javascript:")
    pyperclip.copy("document.title=Math.round(window.scrollY)+'|'+Math.round(document.documentElement.scrollHeight)+'|'+Math.round(window.innerHeight);void(0);")
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    time.sleep(0.5)
    
    win = gw.getActiveWindow()
    if win:
        print(f"Title after injection: {win.title}")
    else:
        print("No active window")

if __name__ == "__main__":
    test()
