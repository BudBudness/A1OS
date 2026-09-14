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
        request_id = request.request_id or str(uuid.uuid4())

        if not self.validate(request):
            result = ExecutionResult(
                request_id,
                ExecutionState.FAILED,
                error="validation_failed",
            )
            self._audit(request, result)
            return result

        if not self.authorize(request):
            result = ExecutionResult(
                request_id,
                ExecutionState.FAILED,
                error="authorization_failed",
            )
            self._audit(request, result)
            return result

        if not self.approve(request):
            result = ExecutionResult(
                request_id,
                ExecutionState.FAILED,
                error="human_approval_required",
            )
            self._audit(request, result)
            return result

        if self.executor is None:
            result = ExecutionResult(
                request_id,
                ExecutionState.FAILED,
                error="executor_not_configured",
            )
            self._audit(request, result)
            return result

        attempts = 0

        while True:
            attempts += 1
            heartbeat = True

            try:
                value = self.executor(request)

                checkpoint = {
                    "request_id": request_id,
                    "attempt": attempts,
                    "timestamp": time.time(),
                }

                if not self.verify(value):
                    raise RuntimeError("verification_failed")

                result = ExecutionResult(
                    request_id=request_id,
                    state=ExecutionState.COMPLETED,
                    result=value,
                    attempts=attempts,
                    heartbeat=heartbeat,
                    checkpoint=checkpoint,
                )
                self._audit(request, result)
                return result

            except Exception as exc:
                if attempts > self.max_retries:
                    result = ExecutionResult(
                        request_id=request_id,
                        state=ExecutionState.FAILED,
                        error=str(exc),
                        attempts=attempts,
                        heartbeat=heartbeat,
                    )
                    self._audit(request, result)
                    return result

    async def execute_async(self, request: ExecutionRequest) -> ExecutionResult:
        request_id = request.request_id or str(uuid.uuid4())

        if not self.validate(request):
            result = ExecutionResult(
                request_id,
                ExecutionState.FAILED,
                error="validation_failed",
            )
            self._audit(request, result)
            return result

        if not self.authorize(request):
            result = ExecutionResult(
                request_id,
                ExecutionState.FAILED,
                error="authorization_failed",
            )
            self._audit(request, result)
            return result

        if not self.approve(request):
            result = ExecutionResult(
                request_id,
                ExecutionState.FAILED,
                error="human_approval_required",
            )
            self._audit(request, result)
            return result

        if self.executor is None:
            result = ExecutionResult(
                request_id,
                ExecutionState.FAILED,
                error="executor_not_configured",
            )
            self._audit(request, result)
            return result

        attempts = 0

        while True:
            attempts += 1
            heartbeat = True

            try:
                value = self.executor(request)
                if inspect.isawaitable(value):
                    value = await value

                checkpoint = {
                    "request_id": request_id,
                    "attempt": attempts,
                    "timestamp": time.time(),
                }

                if not self.verify(value):
                    raise RuntimeError("verification_failed")

                result = ExecutionResult(
                    request_id=request_id,
                    state=ExecutionState.COMPLETED,
                    result=value,
                    attempts=attempts,
                    heartbeat=heartbeat,
                    checkpoint=checkpoint,
                )
                self._audit(request, result)
                return result

            except Exception as exc:
                if attempts > self.max_retries:
                    result = ExecutionResult(
                        request_id=request_id,
                        state=ExecutionState.FAILED,
                        error=str(exc),
                        attempts=attempts,
                        heartbeat=heartbeat,
                    )
                    self._audit(request, result)
                    return result

    def retry(self, request: ExecutionRequest) -> ExecutionResult:
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

        self._transitions.setdefault(request_id, []).append(state)
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
