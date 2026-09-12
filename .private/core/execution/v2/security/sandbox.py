from typing import Any, Dict, Optional

from core.lifecycle import ExecutionBroker, ExecutionRequest


class Sandbox:
    """Lifecycle-governed sandbox execution adapter."""

    def __init__(self, broker: Optional[ExecutionBroker] = None):
        self.broker = broker or ExecutionBroker(executor=self._execute_command)

    async def _execute_command(self, request):
        import asyncio

        proc = await asyncio.create_subprocess_exec(
            *[str(x) for x in request.payload["cmd_list"]],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        return {
            "returncode": proc.returncode,
            "stdout": stdout.decode(errors="replace"),
            "stderr": stderr.decode(errors="replace"),
        }

    async def execute(
        self,
        cmd_list,
        *,
        approval_token: Optional[str] = None,
        request_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ):
        if not isinstance(cmd_list, (list, tuple)) or not cmd_list:
            raise ValueError("cmd_list must be a non-empty command list")

        request = ExecutionRequest(
            command=" ".join(str(x) for x in cmd_list),
            payload={
                "capability": "sandbox.execute",
                "cmd_list": [str(x) for x in cmd_list],
                **(payload or {}),
            },
            approval_token=approval_token,
            request_id=request_id,
        )

        return await self.broker.execute_async(request)
