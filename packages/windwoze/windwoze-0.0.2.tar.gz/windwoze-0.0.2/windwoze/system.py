import os
import ctypes
def shutdown():
    os.system("shutdown /s /t 0")

def lock():
    ctypes.windll.user32.LockWorkStation()
