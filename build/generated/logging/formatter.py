import json

class DiagnosticLogFormatter:
    @staticmethod
    def format_json(log_entry):
        return json.dumps(log_entry)

    @staticmethod
    def format_text(log_entry):
        return f"{log_entry['time']} | {log_entry['level']} | {log_entry['subsystem']} | {log_entry['message']}"