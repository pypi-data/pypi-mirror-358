import subprocess
import ctypes

def launch_app(path, args=None):
    cmd = [path]
    if args:
        cmd += args
    return subprocess.Popen(cmd)

