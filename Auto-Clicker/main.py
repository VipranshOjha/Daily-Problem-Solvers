import pyautogui
import time
import datetime

def click_at_coordinates(x, y, clicks=1, interval=0.0):
    
    pyautogui.moveTo(x, y)
    pyautogui.click(x=x, y=y, clicks=clicks, interval=interval)
    print(f"Clicked at coordinates ({x}, {y})")

def wait_until_time(target_hour, target_minute, target_second=0):

    now = datetime.datetime.now()
    target_time = now.replace(hour=target_hour, minute=target_minute, second=target_second, microsecond=0)
    
    if now > target_time:
        return False
    
    wait_seconds = (target_time - now).total_seconds()
    
    print(f"Current time: {now.strftime('%H:%M:%S')}")
    print(f"Target time: {target_time.strftime('%H:%M:%S')}")
    print(f"Waiting for {wait_seconds:.1f} seconds until {target_time.strftime('%I:%M:%S %p')}...")
    
    time.sleep(wait_seconds)
    return True

if __name__ == "__main__":
    # Insert coordinates 
    x_coordinate = 500  
    y_coordinate = 500  
    
    # Insert time (24-hour format)
    target_hour = 22   
    target_minute = 20
    target_second = 0   
    
    screen_width, screen_height = pyautogui.size()
    print(f"Screen resolution: {screen_width}x{screen_height}")
    
    success = wait_until_time(target_hour, target_minute, target_second)
    
    if success:
        click_at_coordinates(x_coordinate, y_coordinate)
    else:
        print("The specified time has already passed for today. Please set a future time.")
