from collections import deque
import json, time

class EventBus:
    def __init__(self):
        self.topics={"events":deque(),"tasks":deque()}

    def publish(self,topic,data):
        self.topics.setdefault(topic,deque()).append({
            "data":data,
            "ts":time.time()
        })

    def consume(self,topic):
        if self.topics.get(topic):
            try:
                return self.topics[topic].popleft()
            except:
                return None
        return None

bus=EventBus()
