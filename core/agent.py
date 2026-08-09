import requests
from lib.file_io import LocalFileProvider

class A1Agent:
    def __init__(self):
        self.fs = LocalFileProvider()
        self.ollama_url = "http://localhost:11434/api/generate"

    def process_task(self, instruction):
        # 1. Ask Ollama for the implementation/logic
        response = requests.post(self.ollama_url, json={
            "model": "llama3",
            "prompt": f"Implement this task: {instruction}. Return only the code.",
            "stream": False
        }).json().get("response", "")
        
        # 2. Apply the code (Requires your approval gate)
        # For full automation, set approved=True ONLY after you trust the output
        print(f"Agent generated code. Applying...")
        return self.fs.write_file("generated_patch.py", response, approved=True)
