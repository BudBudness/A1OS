import asyncio
import json
import logging
from core.kernel import A1OSKernel
from core.scheduler import Scheduler

logging.basicConfig(level=logging.INFO)

async def main():
    kernel = A1OSKernel()
    scheduler = Scheduler()
    await asyncio.gather(kernel.loop(), scheduler.run())

if __name__ == "__main__":
    asyncio.run(main())
