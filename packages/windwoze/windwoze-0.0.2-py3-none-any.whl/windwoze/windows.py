import ctypes
from ctypes import wintypes

def find_window(title):
    return ctypes.windll.user32.FindWindowW(None, title)

def bring_to_front(hwnd):
    ctypes.windll.user32.ShowWindow(hwnd, 5)
    ctypes.windll.user32.SetForegroundWindow(hwnd)
