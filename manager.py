import os, time
from core.agent import A1Agent

class SystemManager:
    def __init__(self):
        self.agent = A1Agent()
        self.task_dir = "data/tasks"

    def run(self):
        print("A1OS Daemon Online. Monitoring data/tasks/...")
        while True:
            tasks = [f for f in os.listdir(self.task_dir) if f.endswith('.txt')]
            for task_file in tasks:
                with open(os.path.join(self.task_dir, task_file), 'r') as f:
                    instruction = f.read()
                    print(f"Processing: {task_file}")
                    self.agent.process_task(instruction)
                os.rename(os.path.join(self.task_dir, task_file), os.path.join("data/archive", task_file))
            time.sleep(5)

if __name__ == "__main__":
    SystemManager().run()
