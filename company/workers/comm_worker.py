from modules.communication.parsers.intent_parser import IntentParser

class CommWorker:
    def __init__(self):
        self.parser = IntentParser()

    def process_message(self, message):
        # Convert raw text into task payload
        task = self.parser.parse(message)
        return task
