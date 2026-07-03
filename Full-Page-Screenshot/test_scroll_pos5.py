import pyautogui
pyautogui.FAILSAFE = False
import pyperclip
import time
import pygetwindow as gw
import subprocess
import os

def test():
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if os.path.exists(chrome_path):
        subprocess.Popen([chrome_path, "https://en.wikipedia.org/wiki/Main_Page"])
        time.sleep(3)
        
    windows = gw.getWindowsWithTitle("Chrome")
    if windows:
        windows[0].activate()
        time.sleep(1)
    
    # Inject listener
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.1)
    pyautogui.write("javascript:")
    pyperclip.copy("window.addEventListener('scroll', () => { document.title = Math.round(window.scrollY) + '_SCROLL'; }); document.title = Math.round(window.scrollY) + '_SCROLL'; void(0);")
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    time.sleep(0.5)
    
    win = gw.getActiveWindow()
    print(f"Title initially: {win.title}")
    
    # Scroll down
    pyautogui.press('pagedown')
    time.sleep(0.5)
    
    win = gw.getActiveWindow()
    print(f"Title after scroll: {win.title}")

if __name__ == "__main__":
    test()
