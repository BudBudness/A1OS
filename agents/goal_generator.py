import time, json
from a1os.bus.event_bus import bus

GOALS=[
    "analyze_system_state",
    "optimize_memory_usage",
    "review_recent_tasks",
    "generate_insights"
]

i=0
while True:
    goal={"goal":GOALS[i%len(GOALS)]}
    bus.publish("tasks",goal)
    i+=1
    time.sleep(5)
