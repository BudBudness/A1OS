import os, time

def watch(process_name):
    while True:
        if os.system(f"pgrep -f {process_name} > /dev/null") != 0:
            os.system(f"python -u {process_name} &")
        time.sleep(5)
