import asyncio

from runtime.engine import A1OSEngine
from runtime.kernel_contract import RuntimeKernelContract


def test_runtime_kernel_contract():
    assert RuntimeKernelContract.validate(A1OSEngine()) is True


def test_engine_worker_registry_is_authoritative():
    async def run():
        engine = A1OSEngine()
        worker = object()

        result = await engine.register_worker("test_worker", worker)

        assert result is worker
        assert engine.worker_registry.get("test_worker") is worker
        assert engine.worker_registry.names() == ("test_worker",)
        assert engine.worker_registry.snapshot() == {"test_worker": worker}

        assert not hasattr(engine, "_workers")

    asyncio.run(run())


def test_worker_registry_rejects_invalid_registration():
    async def run():
        engine = A1OSEngine()

        try:
            await engine.register_worker("", object())
        except ValueError as exc:
            assert str(exc) == "Worker name must be a non-empty string"
        else:
            raise AssertionError("Expected ValueError")

    asyncio.run(run())
