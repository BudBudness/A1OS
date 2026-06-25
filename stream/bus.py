from collections import defaultdict, deque
import time

class StreamBus:
    def __init__(self):
        self.topics=defaultdict(deque)

    def publish(self,topic,msg):
        self.topics[topic].append({
            "msg":msg,
            "ts":time.time()
        })

    def consume(self,topic):
        if self.topics[topic]:
            return self.topics[topic].popleft()
        return None

bus=StreamBus()
