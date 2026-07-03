import pyautogui
import pyperclip
import time
import pygetwindow as gw
import os

def test_title_injection():
    # Give user 3 seconds to focus Chrome
    print("Please focus Chrome in the next 3 seconds...")
    time.sleep(3)
    
    # Store original title (from active window)
    active = gw.getActiveWindow()
    print(f"Active window: {active.title}")
    
    js_payload = "document.title=Math.round(window.scrollY)+'_'+Math.round(document.documentElement.scrollHeight)+'_SCROLL';void(0);"
    pyperclip.copy(js_payload)
    
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.05)
    pyautogui.write("javascript:")
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    
    # Wait a bit for title to change
    time.sleep(0.5)
    
    # Find window with _SCROLL in title
    windows = gw.getAllWindows()
    for w in windows:
        if "_SCROLL" in w.title:
            print(f"Found scroll info in title: {w.title}")
            return
            
    print("Failed to find scroll info in title.")

if __name__ == "__main__":
    test_title_injection()
