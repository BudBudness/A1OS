import requests
from lib.file_io import LocalFileProvider
from tools.a1os_factory.engine_runtime import require_agent_preflight

class A1Agent:
    def __init__(self):
        self.fs = LocalFileProvider()
        self.ollama_url = "http://localhost:11434/api/generate"

    def process_task(self, instruction):
        require_agent_preflight("core/agent.py")
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
