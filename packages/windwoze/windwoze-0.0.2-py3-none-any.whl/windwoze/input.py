import ctypes
import time

def key_press(hex_key_code):
    ctypes.windll.user32.keybd_event(hex_key_code, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(hex_key_code, 0, 2, 0)

def move_mouse(x, y):
    ctypes.windll.user32.SetCursorPos(x, y)

def click_mouse():
    ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)  # Mouse left down
    ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)  # Mouse left up
