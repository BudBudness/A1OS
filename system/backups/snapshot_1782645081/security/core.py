class SovereignSecuritySandbox:
    def __init__(self):
        self.blacklisted_tokens = ["exec", "eval", "os.system", "__import__"]
    def audit_string(self, payload_str):
        for token in self.blacklisted_tokens:
            if token in payload_str:
                return False, f"Malicious syntax token intercepted: '{token}'"
        return True, "SAFE"
