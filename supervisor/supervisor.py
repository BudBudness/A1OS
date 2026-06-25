import time, subprocess

def check_process(name):
    import os
    return os.system(f"pgrep -f {name} > /dev/null") == 0

while True:
    if not check_process("server.py"):
        subprocess.Popen(["python","-u","a1os/api/server.py"])
    if not check_process("goal_generator"):
        subprocess.Popen(["python","-u","a1os/agents/goal_generator.py"])
    time.sleep(5)
