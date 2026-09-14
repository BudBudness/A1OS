from core.lifecycle import ExecutionBroker, ExecutionRequest, ExecutionState


def test_lifecycle_records_terminal_state_and_evidence():
    broker = ExecutionBroker(
        authorizer=lambda request: True,
        executor=lambda request: {"ok": True},
    )
    request = ExecutionRequest(
        command="evidence-test",
        approval_token="approved",
        request_id="evidence-001",
    )

    result = broker.execute(request)

    assert result.state == ExecutionState.COMPLETED
    history = broker.transition_history(request.request_id)
    evidence = broker.evidence(request.request_id)

    assert history
    assert history[-1] == ExecutionState.COMPLETED
    assert evidence
    assert evidence[-1]["request_id"] == request.request_id
    assert evidence[-1]["state"] == ExecutionState.COMPLETED.value


def test_failed_execution_records_terminal_evidence():
    broker = ExecutionBroker()
    request = ExecutionRequest(
        command="blocked",
        request_id="evidence-002",
    )

    result = broker.execute(request)

    assert result.state == ExecutionState.FAILED
    assert broker.transition_history(request.request_id)[-1] == ExecutionState.FAILED
    assert broker.evidence(request.request_id)[-1]["state"] == ExecutionState.FAILED.value

def test_lifecycle_transition_order():
    broker = ExecutionBroker(
        authorizer=lambda request: True,
        executor=lambda request: {"ok": True},
    )
    request = ExecutionRequest(
        command="transition-order-test",
        approval_token="approved",
        request_id="transition-order-001",
    )
    result = broker.execute(request)
    assert result.state == ExecutionState.COMPLETED
    assert [state.value for state in broker.transition_history(request.request_id)] == [
        "planned", "validated", "authorized", "approved",
        "dispatched", "executing", "checkpointed", "completed",
    ]
