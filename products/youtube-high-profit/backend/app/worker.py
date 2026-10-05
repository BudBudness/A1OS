from .main import demo_run, GenerateRequest
if __name__ == "__main__":
    demo_run("worker-demo", GenerateRequest(topic="worker smoke test"))
