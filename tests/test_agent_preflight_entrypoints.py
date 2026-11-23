"""Tests for deterministic A1OS agent-entry preflight enforcement."""
from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import unittest
from unittest.mock import patch

from tools.a1os_factory import engine_runtime


class AgentPreflightEntrypointTests(unittest.TestCase):
    @patch("tools.a1os_factory.engine_runtime.subprocess.run")
    def test_preflight_prints_instruction_receipt(self, run):
        run.return_value = subprocess.CompletedProcess(
            args=["python", "check_agent_instructions.py"],
            returncode=0,
            stdout="A1OS_AGENT_PREFLIGHT=PASS\n",
            stderr="",
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            engine_runtime.require_agent_preflight("tools/a1os_factory/")
        self.assertIn("A1OS_AGENT_PREFLIGHT=PASS", output.getvalue())
        args = run.call_args.args[0]
        self.assertIn("--preflight", args)
        self.assertIn("--for-path", args)
        self.assertEqual(args[-1], "tools/a1os_factory/")

    @patch("tools.a1os_factory.engine_runtime.subprocess.run")
    def test_preflight_failure_stops_execution(self, run):
        run.return_value = subprocess.CompletedProcess(
            args=["python", "check_agent_instructions.py"],
            returncode=1,
            stdout="",
            stderr="PRE-FLIGHT BLOCKED: provider conflict\n",
        )
        with self.assertRaises(SystemExit) as raised:
            engine_runtime.require_agent_preflight("core/agent.py")
        self.assertEqual(raised.exception.code, 1)

    def test_all_internal_agent_entrypoints_invoke_preflight(self):
        root = engine_runtime.Path(__file__).resolve().parents[1]
        entrypoints = {
            "tools/a1os_factory/engine_runtime.py": 'require_agent_preflight("tools/a1os_factory/")',
            "tools/a1os_factory/autonomous_agent_operations_runtime/agent_operations_engine.py": 'require_agent_preflight("tools/a1os_factory/autonomous_agent_operations_runtime/")',
            "tools/a1os_factory/ai_agent_operating_layer/ai_agent_operating_engine.py": 'require_agent_preflight("tools/a1os_factory/ai_agent_operating_layer/")',
            "core/agent.py": 'require_agent_preflight("core/agent.py")',
        }
        for relative, marker in entrypoints.items():
            with self.subTest(entrypoint=relative):
                self.assertIn(marker, (root / relative).read_text(encoding="utf-8"))

    @patch("tools.a1os_factory.engine_runtime.FactoryEngine.run")
    @patch("tools.a1os_factory.engine_runtime.require_agent_preflight")
    def test_factory_cli_preflights_before_engine_run(self, preflight, run):
        run.return_value = {"status": "planned"}
        engine = engine_runtime.make_engine("test", "test")
        old_argv = sys.argv
        try:
            sys.argv = ["engine", "sample-product"]
            with contextlib.redirect_stdout(io.StringIO()):
                engine_runtime.cli(engine)
        finally:
            sys.argv = old_argv
        preflight.assert_called_once_with("tools/a1os_factory/")
        run.assert_called_once_with("sample-product", {}, None)


if __name__ == "__main__":
    unittest.main()
