import asyncio

from modules.finance import Finance
from modules.executive_dashboard import Executive_dashboard


async def run_test():
    finance = Finance()
    dashboard = Executive_dashboard()

    print(await finance.execute("refresh_metrics"))
    print(dashboard.execute("refresh_metrics"))


if __name__ == "__main__":
    asyncio.run(run_test())
