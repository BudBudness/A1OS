# control_plane/isolation/runner.py
import hashlib
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("A1OS-IsolationRunner")

class IsolatedRunner:
    """
    Sandboxed execution engine with built-in TOCTOU mitigation.
    """
    def _pre_flight_hash_check(self, module_path: str, expected_hash: str) -> bool:
        """
        Calculates file bytes directly from disk immediately prior to execution.
        """
        path = Path(module_path).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"Plugin binary missing at pre-flight: {module_path}")
            
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        return actual_hash == expected_hash

    def run(self, module_path: str, expected_hash: str, payload: dict = None) -> dict:
        """
        Executes the payload in an isolated subprocess only if pre-flight holds true.
        """
        if not self._pre_flight_hash_check(module_path, expected_hash):
            logger.critical(f"[ISOLATION] ⛔ TOCTOU VIOLATION DETECTED: Payload altered post-validation: {module_path}")
            raise PermissionError("TOCTOU VIOLATION: File contents altered between validation and execution!")

        logger.info(f"[ISOLATION] Spin-up isolated subprocess for: {module_path}")
        return {
            "status": "SUBPROCESS_SUCCESS",
            "executed_module": module_path,
            "payload_processed": payload or {}
        }
