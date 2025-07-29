import subprocess

def run(cmd):
    subprocess.run(["cmd.exe", "/c", cmd])

def powershell(ps_cmd):
    subprocess.run(["powershell", "-Command", ps_cmd])
