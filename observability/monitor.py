import time
from a1os.stream.bus import bus

def stats():
    while True:
        print({
            "tasks":len(bus.topics["tasks"]),
            "results":len(bus.topics["results"])
        })
        time.sleep(5)
