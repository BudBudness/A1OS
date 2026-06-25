import time
from a1os.bus.event_bus import bus

queue=[]

while True:
    task=bus.consume("tasks")
    if task:
        queue.append(task)

    if queue:
        t=queue.pop(0)
        bus.publish("events",{"executed":t})

    time.sleep(2)
