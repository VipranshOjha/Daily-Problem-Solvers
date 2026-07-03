import pyautogui
import pyperclip
import time
import pygetwindow as gw

def get_scroll_pos():
    windows = gw.getWindowsWithTitle("Google Chrome")
    if not windows:
        print("No chrome window")
        return
        
    win = windows[0]
    win.activate()
    time.sleep(1)
    
    # Empty clipboard
    pyperclip.copy("")
    
    # Try typing javascript snippet
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.1)
    pyautogui.write("javascript:navigator.clipboard.writeText(Math.round(window.scrollY).toString());", interval=0.01)
    pyautogui.press('enter')
    time.sleep(0.5) # Wait for clipboard write
    
    val = pyperclip.paste()
    print(f"Clipboard has: '{val}'")

get_scroll_pos()
