import asyncio
import inspect

def pytest_pyfunc_call(pyfuncitem):
    testfunction = pyfuncitem.obj

    if inspect.iscoroutinefunction(testfunction):
        kwargs = {
            name: pyfuncitem.funcargs[name]
            for name in pyfuncitem._fixtureinfo.argnames
            if name in pyfuncitem.funcargs
        }
        asyncio.run(testfunction(**kwargs))
        return True

    return None
