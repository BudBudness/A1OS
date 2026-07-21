# core/kernel.py
class Kernel:
    def __init__(self):
        self.workers = {}
        self.register_workers()
    
    def register_workers(self):
        # Register analytics worker
        try:
            from workers.analytics import AnalyticsWorker
            self.workers['analytics'] = AnalyticsWorker()
        except ImportError:
            # Create inline worker if file doesn't exist
            class SimpleAnalyticsWorker:
                def __call__(self, data):
                    return {"status": "analytics_processed", "data": data}
            self.workers['analytics'] = SimpleAnalyticsWorker()
    
    def process_input(self, data):
        target = data.get('target', 'default')
        
        if target not in self.workers:
            raise KeyError(f"Worker '{target}' not found")
        
        worker = self.workers[target]
        return worker(data)
    
    async def process_input_async(self, data):
        # Async wrapper for the sync process_input
        import asyncio
        return await asyncio.to_thread(self.process_input, data)
