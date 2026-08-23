from __future__ import annotations

import hashlib
import json
import time
import uuid
from pathlib import Path
from typing import Any


class ApprovalDenied(PermissionError):
    pass


class HumanApprovalController:
    """
    Explicit human-approval boundary for consequential A1OS execution.

    Security properties:
      - approval is bound to exact task/capability/action/entity
      - client-supplied approval flags are never trusted
      - approvals expire
      - provenance must be present and cryptographically valid
      - approval cannot authorize a different action
      - state is persisted locally for auditability
      - no execution is performed by this controller
    """

    def __init__(self, state_dir: str = "runtime/approvals") -> None:
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _canonical(data: dict[str, Any]) -> str:
        return json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
        )

    @classmethod
    def _hash(cls, data: dict[str, Any]) -> str:
        return hashlib.sha256(
            cls._canonical(data).encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _require_human_provenance(provenance: Any) -> None:
        if not isinstance(provenance, dict):
            raise ApprovalDenied("Missing authorization provenance")

        if provenance.get("requires_human") is not True:
            raise ApprovalDenied(
                "Approval requires requires_human=True provenance"
            )

        if provenance.get("verified") is not False:
            raise ApprovalDenied(
                "Approval provenance must initially be unverified"
            )

        if not provenance.get("provenance_id"):
            raise ApprovalDenied("Missing provenance_id")

        if not provenance.get("capability"):
            raise ApprovalDenied("Missing capability")

        if not provenance.get("entity_id"):
            raise ApprovalDenied("Missing entity_id")

        if "action" not in provenance:
            raise ApprovalDenied("Missing action")

        if provenance.get("decision") != "human_required":
            raise ApprovalDenied(
                "Only human_required decisions may enter approval"
            )

    def request(
        self,
        *,
        task_id: str,
        capability: str,
        entity_id: str,
        action: str,
        provenance: dict[str, Any],
        requested_by: str = "a1os",
        ttl_seconds: int = 300,
    ) -> dict[str, Any]:

        if not task_id:
            raise ValueError("task_id is required")

        if not capability:
            raise ValueError("capability is required")

        self._require_human_provenance(provenance)

        approval_id = f"approval-{uuid.uuid4()}"
        now = time.time()

        record = {
            "approval_id": approval_id,
            "task_id": task_id,
            "capability": capability,
            "entity_id": entity_id,
            "action": action,
            "requested_by": requested_by,
            "status": "pending",
            "created_at": now,
            "expires_at": now + max(1, int(ttl_seconds)),
            "provenance": provenance,
        }

        record["record_hash"] = self._hash(record)

        path = self.state_dir / f"{approval_id}.json"
        path.write_text(
            json.dumps(record, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        return {
            "status": "pending",
            "approval_id": approval_id,
            "task_id": task_id,
            "expires_at": record["expires_at"],
        }

    def approve(
        self,
        *,
        approval_id: str,
        approver_id: str,
    ) -> dict[str, Any]:

        if not approver_id:
            raise ApprovalDenied("Human approver identity is required")

        path = self.state_dir / f"{approval_id}.json"

        if not path.exists():
            raise ApprovalDenied("Approval request not found")

        record = json.loads(path.read_text(encoding="utf-8"))

        unsigned = dict(record)
        supplied_hash = unsigned.pop("record_hash", None)

        if supplied_hash != self._hash(unsigned):
            raise ApprovalDenied("Approval record integrity check failed")

        if record.get("status") != "pending":
            raise ApprovalDenied(
                f"Approval is not pending: {record.get('status')}"
            )

        if time.time() >= float(record["expires_at"]):
            record["status"] = "expired"
            path.write_text(
                json.dumps(record, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            raise ApprovalDenied("Approval request expired")

        provenance = record.get("provenance")

        if not isinstance(provenance, dict):
            raise ApprovalDenied("Approval provenance missing")

        if provenance.get("requires_human") is not True:
            raise ApprovalDenied("Human authorization provenance required")

        if provenance.get("decision") != "human_required":
            raise ApprovalDenied("Invalid authorization decision")

        if provenance.get("verified") is not False:
            raise ApprovalDenied(
                "Approval requires unverified authorization provenance"
            )

        record["status"] = "approved"
        record["approver_id"] = approver_id
        record["approved_at"] = time.time()

        record["approval_provenance"] = {
            "approval_id": approval_id,
            "approver_id": approver_id,
            "task_id": record["task_id"],
            "capability": record["capability"],
            "entity_id": record["entity_id"],
            "action": record["action"],
            "approved_at": record["approved_at"],
        }

        record["approval_provenance"]["record_hash"] = self._hash(
            record["approval_provenance"]
        )

        record.pop("record_hash", None)
        record["record_hash"] = self._hash(record)

        path.write_text(
            json.dumps(record, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        return {
            "status": "approved",
            "approval_id": approval_id,
            "task_id": record["task_id"],
            "capability": record["capability"],
            "action": record["action"],
            "approver_id": approver_id,
        }

    def consume(
        self,
        *,
        approval_id: str,
        task_id: str,
        capability: str,
        entity_id: str,
        action: str,
    ) -> dict[str, Any]:

        path = self.state_dir / f"{approval_id}.json"

        if not path.exists():
            raise ApprovalDenied("Approval request not found")

        record = json.loads(path.read_text(encoding="utf-8"))

        supplied_hash = record.pop("record_hash", None)
        if supplied_hash != self._hash(record):
            raise ApprovalDenied("Approval record integrity check failed")
        record["record_hash"] = supplied_hash

        if record.get("status") != "approved":
            raise ApprovalDenied("Human approval has not been granted")

        if time.time() >= float(record["expires_at"]):
            raise ApprovalDenied("Approved authorization has expired")

        bindings = {
            "task_id": task_id,
            "capability": capability,
            "entity_id": entity_id,
            "action": action,
        }

        for key, expected in bindings.items():
            if record.get(key) != expected:
                raise ApprovalDenied(
                    f"Approval binding mismatch: {key}"
                )

        approval_provenance = record.get("approval_provenance")

        if not isinstance(approval_provenance, dict):
            raise ApprovalDenied("Approval provenance missing")

        provenance_hash = approval_provenance.get("record_hash")
        unsigned_provenance = dict(approval_provenance)
        unsigned_provenance.pop("record_hash", None)

        if provenance_hash != self._hash(unsigned_provenance):
            raise ApprovalDenied(
                "Approval provenance integrity check failed"
            )

        # Single-use approval.
        record["status"] = "consumed"
        record["consumed_at"] = time.time()

        record.pop("record_hash", None)
        record["record_hash"] = self._hash(record)

        path.write_text(
            json.dumps(record, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        return {
            "authorized": True,
            "status": "approved",
            "approval_id": approval_id,
            "task_id": task_id,
            "capability": capability,
            "entity_id": entity_id,
            "action": action,
            "approver_id": record["approval_provenance"]["approver_id"],
            "approval_provenance": record["approval_provenance"],
        }

    def get(self, approval_id: str) -> dict[str, Any] | None:
        path = self.state_dir / f"{approval_id}.json"

        if not path.exists():
            return None

        return json.loads(path.read_text(encoding="utf-8"))


approval_controller = HumanApprovalController()
