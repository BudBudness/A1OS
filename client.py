import requests
import sys

def send_command(cmd: str):
    response = requests.post("http://localhost:3000/api/v1/command", json={"command": cmd})
    print(response.json())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        send_command(sys.argv[1])
