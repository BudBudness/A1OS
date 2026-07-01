import time
import uuid

class EventMessageEnvelope:
    def __init__(self, event_type, data):
        self.envelope_id = str(uuid.uuid4())
        self.event_type = event_type
        self.timestamp = time.time()
        self.data = data

    def package(self):
        return {
            "id": self.envelope_id,
            "type": self.event_type,
            "time": self.timestamp,
            "payload": self.data
        }