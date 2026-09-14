from __future__ import annotations
import inspect

import time
import uuid
from typing import Any, Callable

from .models import ExecutionRequest, ExecutionResult, ExecutionState
from core.recovery.checkpoints import CheckpointStore


class ExecutionBroker:
    """
    Approval-gated lifecycle broker.

    Lifecycle:
      plan -> validate -> authorize -> approval
      -> dispatch -> execute -> checkpoint -> verify -> audit

    The broker does not manufacture approval. Approval must be supplied
    explicitly by the caller.
    """

    def __init__(
        self,
        *,
        validator: Callable[[ExecutionRequest], bool] | None = None,
        authorizer: Callable[[ExecutionRequest], bool] | None = None,
        executor: Callable[[ExecutionRequest], Any] | None = None,
        verifier: Callable[[Any], bool] | None = None,
        auditor: Callable[[dict], None] | None = None,
        max_retries: int = 0,
        heartbeat_interval: float = 0.0,
    ):
        self.validator = validator or (lambda request: bool(request.command))
        self.authorizer = authorizer or (lambda request: bool(request.approval_token))
        self.executor = executor
        self.verifier = verifier or (lambda result: True)
        self.auditor = auditor
        self._transitions = {}
        self._evidence = {}
        self._evidence_store = CheckpointStore()
        self.max_retries = max(0, int(max_retries))
        self.heartbeat_interval = max(0.0, float(heartbeat_interval))

    def _transition(self, request_id: str, state: ExecutionState, **data):
        history = self._transitions.setdefault(request_id, [])
        if not history or history[-1] != state:
            history.append(state)
        evidence = {
            "request_id": request_id,
            "state": state.value,
            **data,
        }
        self._evidence.setdefault(request_id, []).append(evidence)
        self._evidence_store.save(f"lifecycle:{request_id}", evidence)
        return evidence

    def plan(self, request: ExecutionRequest) -> ExecutionResult:
        request_id = request.request_id or str(uuid.uuid4())
        return ExecutionResult(request_id, ExecutionState.PLANNED)

    def validate(self, request: ExecutionRequest) -> bool:
        return bool(self.validator(request))

    def authorize(self, request: ExecutionRequest) -> bool:
        return bool(self.authorizer(request))

    def approve(self, request: ExecutionRequest) -> bool:
        return bool(request.approval_token)

    def dispatch(self, request: ExecutionRequest) -> ExecutionResult:
        return self.execute(request)

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        request_id = request.request_id
        attempts = 0

        if request_id is not None:
            self._transition(request_id, ExecutionState.PLANNED)

        try:
            if self.validate(request) is False:
                raise RuntimeError("validation_failed")
            if request_id is not None:
                self._transition(request_id, ExecutionState.VALIDATED)

            if self.authorize(request) is False:
                raise RuntimeError("authorization_failed")
            if request_id is not None:
                self._transition(request_id, ExecutionState.AUTHORIZED)

            if self.approve(request) is False:
                raise RuntimeError("human_approval_required")
            if request_id is not None:
                self._transition(request_id, ExecutionState.APPROVED)

        except Exception as exc:
            result = ExecutionResult(
                request_id=request_id,
                state=ExecutionState.FAILED,
                error=str(exc),
                attempts=attempts,
            )
            self._audit(request, result)
            return result

        while True:
            attempts += 1
            try:
                if request_id is not None:
                    self._transition(request_id, ExecutionState.DISPATCHED)
                    self._transition(request_id, ExecutionState.EXECUTING)

                if self.executor is None:
                    raise RuntimeError("executor_not_configured")

                value = self.executor(request)

                if request_id is not None:
                    self._transition(request_id, ExecutionState.CHECKPOINTED)
                    self._transition(request_id, ExecutionState.COMPLETED)

                result = ExecutionResult(
                    request_id=request_id,
                    state=ExecutionState.COMPLETED,
                    result=value,
                    attempts=attempts,
                )
                self._audit(request, result)
                return result

            except Exception as exc:
                if attempts <= self.max_retries:
                    if request_id is not None:
                        self._transition(request_id, ExecutionState.RETRYING)
                    continue

                result = ExecutionResult(
                    request_id=request_id,
                    state=ExecutionState.FAILED,
                    error=str(exc),
                    attempts=attempts,
                )
                self._audit(request, result)
                return result

    async def execute_async(self, request: ExecutionRequest) -> ExecutionResult:
        request_id = request.request_id
        if request_id is not None:
            self._transition(request_id, ExecutionState.PLANNED)
        try:
            if self.validate(request) is False:
                raise RuntimeError("validation_failed")
            if request_id is not None:
                self._transition(request_id, ExecutionState.VALIDATED)

            if self.authorize(request) is False:
                raise RuntimeError("authorization_failed")
            if request_id is not None:
                self._transition(request_id, ExecutionState.AUTHORIZED)

            if self.approve(request) is False:
                raise RuntimeError("human_approval_required")
            if request_id is not None:
                self._transition(request_id, ExecutionState.APPROVED)

            if self.executor is None:
                raise RuntimeError("executor_not_configured")

            if request_id is not None:
                self._transition(request_id, ExecutionState.DISPATCHED)
                self._transition(request_id, ExecutionState.EXECUTING)

            value = self.executor(request)
            if hasattr(value, "__await__"):
                value = await value

            result = ExecutionResult(
                request_id=request_id,
                state=ExecutionState.COMPLETED,
                result=value,
                attempts=1,
            )
            self._audit(request, result)
            return result

        except Exception as exc:
            result = ExecutionResult(
                request_id=request_id,
                state=ExecutionState.FAILED,
                error=str(exc),
                attempts=0,
            )
            self._audit(request, result)
            return result

    def retry(self, request: ExecutionRequest) -> ExecutionResult:
        if request.request_id is not None:
            self._transition(request.request_id, ExecutionState.RETRYING)
        return self.execute(request)

    def checkpoint(self, request_id: str, state: ExecutionState, **data):
        return {
            "request_id": request_id,
            "state": state.value,
            "timestamp": time.time(),
            **data,
        }


    def transition_history(self, request_id: str) -> list[ExecutionState]:
        return list(self._transitions.get(request_id, []))

    def evidence(self, request_id: str) -> list[dict]:
        return list(self._evidence.get(request_id, []))

    def _record_state(self, request_id: str, state: ExecutionState, **data):
        evidence = {
            "request_id": request_id,
            "state": state.value,
            **data,
        }

        history = self._transitions.setdefault(request_id, [])
        if not history or history[-1] != state:
            history.append(state)
        self._evidence.setdefault(request_id, []).append(evidence)

        self._evidence_store.save(
            f"lifecycle:{request_id}",
            evidence,
        )

    def heartbeat(self, request_id: str) -> dict:
        return {
            "request_id": request_id,
            "timestamp": time.time(),
            "alive": True,
        }

    def verify(self, value: Any) -> bool:
        return bool(self.verifier(value))

    def audit(self, request: ExecutionRequest, result: ExecutionResult) -> None:
        self._audit(request, result)

    def _audit(self, request: ExecutionRequest, result: ExecutionResult) -> None:
        request_id = result.request_id
        if request_id is not None:
            self._record_state(
                request_id,
                result.state,
                result=result.result,
                error=result.error,
                attempts=result.attempts,
            )

        if self.auditor is None:
            return

        self.auditor(
            {
                "request_id": result.request_id,
                "command": request.command,
                "state": result.state.value,
                "attempts": result.attempts,
                "error": result.error,
                "timestamp": time.time(),
            }
        )
