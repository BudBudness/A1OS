import re

class InputSanitizer:
    def __init__(self):
        # Strict alphanumeric character restriction matchers
        self.clean_pattern = re.compile(r'[^a-zA-Z0-9_=\-,. ]')

    def sanitize_command(self, raw_string):
        if not raw_string:
            return ""
        return self.clean_pattern.sub("", raw_string).strip()