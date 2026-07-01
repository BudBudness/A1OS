class DeterministicInterpreter:
    def parse_intent(self, raw_text):
        cleaned = raw_text.strip().upper()
        if not cleaned:
            return "UNKNOWN", {}
            
        # Fast split for command/parameter boundaries
        parts = cleaned.split(" ", 1)
        command = parts[0]
        params = {}
        
        if len(parts) > 1:
            # Basic key-value pair syntax extraction helper (key=val)
            for pair in parts[1].split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    params[k.strip().lower()] = v.strip()
                    
        return command, params