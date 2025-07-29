from ctypes import windll

def send_enter(hwnd):
    WM_KEYDOWN = 0x0100
    VK_RETURN = 0x0D
    windll.user32.PostMessageW(hwnd, WM_KEYDOWN, VK_RETURN, 0)
