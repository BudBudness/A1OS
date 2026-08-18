class IntentParser:
    def parse(self, text: str) -> dict:
        if not isinstance(text, str):
            raise TypeError("Intent text must be a string")

        text = text.strip()
        if not text:
            raise ValueError("Intent text cannot be empty")

        parts = text.split(maxsplit=1)
        intent = parts[0].lower()
        payload = parts[1] if len(parts) > 1 else ""

        return {
            "intent": intent,
            "payload": payload,
            "raw": text,
        }

    def parse_intent(self, text: str) -> dict:
        return self.parse(text)
