import subprocess
import os

class Sandbox:
    def execute(self, cmd_list):
        wrapped_cmd = ["unshare", "-m", "-u", "-i", "-n", "-p", "-f"] + cmd_list
        return subprocess.run(wrapped_cmd, capture_output=True, text=True)
