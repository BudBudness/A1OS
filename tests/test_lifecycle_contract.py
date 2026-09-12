from core.lifecycle import ExecutionBroker, ExecutionRequest, ExecutionState


def test_validation_blocks_empty_command():
    broker = ExecutionBroker(executor=lambda request: True)
    result = broker.execute(
        ExecutionRequest(command="", approval_token="approved")
    )
    assert result.state == ExecutionState.FAILED
    assert result.error == "validation_failed"


def test_execution_requires_approval():
    broker = ExecutionBroker(executor=lambda request: True)
    result = broker.execute(
        ExecutionRequest(command="safe")
    )
    assert result.state == ExecutionState.FAILED
    assert result.error == "authorization_failed"


def test_execution_requires_human_approval_token():
    broker = ExecutionBroker(
        authorizer=lambda request: True,
        executor=lambda request: True,
    )
    result = broker.execute(
        ExecutionRequest(command="protected")
    )
    assert result.state == ExecutionState.FAILED
    assert result.error == "human_approval_required"


def test_execution_completes_after_approval():
    broker = ExecutionBroker(
        authorizer=lambda request: True,
        executor=lambda request: {"executed": True},
    )
    result = broker.execute(
        ExecutionRequest(
            command="approved-command",
            approval_token="human-approved",
        )
    )
    assert result.state == ExecutionState.COMPLETED
    assert result.result["executed"] is True


def test_retry_contract():
    calls = {"count": 0}

    def executor(request):
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("temporary")
        return True

    broker = ExecutionBroker(
        authorizer=lambda request: True,
        executor=executor,
        max_retries=1,
    )

    result = broker.execute(
        ExecutionRequest(
            command="retryable",
            approval_token="approved",
        )
    )

    assert result.state == ExecutionState.COMPLETED
    assert result.attempts == 2


def test_heartbeat_contract():
    broker = ExecutionBroker()
    heartbeat = broker.heartbeat("test-request")
    assert heartbeat["request_id"] == "test-request"
    assert heartbeat["alive"] is True




def test_async_executor_bridge():
    import asyncio
    from core.lifecycle import ExecutionBroker, ExecutionRequest, ExecutionState

    async def executor(request):
        return {"bridge": "runtime", "request_id": request.request_id}

    async def run():
        broker = ExecutionBroker(
            executor=executor,
            authorizer=lambda request: True,
        )

        request = ExecutionRequest(
            command="runtime.probe",
            payload={"probe": True},
            approval_token="approved",
            request_id="async-runtime-bridge",
        )

        result = await broker.execute_async(request)

        assert result.state == ExecutionState.COMPLETED
        assert result.result["bridge"] == "runtime"
        assert result.attempts == 1

    asyncio.run(run())
