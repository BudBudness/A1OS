import logging

class Executor:
    async def orchestrate(self, task):
        logging.info(f"Orchestrating task: {task.get('action')}")
