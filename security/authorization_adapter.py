import hashlib
import json
import time
import uuid


class AuthorizationAdapter:
    READ_ONLY_CAPABILITIES = {
        "health",
        "observability",
        "digital_world_model",
        "digital_world_graph",
        "digital_world_query",
        "digital_world_state",
        "digital_world_intelligence",
    }

    KNOWN_CAPABILITIES = {
        "digital_world_recovery",
        "read_capability",
        "write_capability",
    }

    POLICY_VERSION = "sovereignty-policy-v1"

    async def authorize(self, capability, kwargs=None):
        kwargs = dict(kwargs or {})

        if capability in self.READ_ONLY_CAPABILITIES:
            return {
                "allowed": True,
                "requires_authorization": False,
                "classification": "read_only",
                "capability": capability,
                "decision": "read_only_allowed",
            }

        entity_id = kwargs.get("entity_id", "primary-device")
        target_action = (
            kwargs.get("action")
            or kwargs.get("target_action")
            or kwargs.get("operation")
            or ""
        )

        if capability not in self.KNOWN_CAPABILITIES:
            return {
                "allowed": False,
                "requires_authorization": True,
                "classification": "consequential",
                "capability": capability,
                "decision": "human_required",
                "reason": "Unknown capability - fail closed",
            }

        authorization = {
            "authorized": True,
            "allowed": True,
            "autonomous_authorization": True,
            "decision": "autonomous_authorization",
            "reason": "Consequential authorization granted.",
            "confidence": 1.0,
            "provenance": {
                "authorization_id": f"auth-{uuid.uuid4()}",
                "entity_id": entity_id,
                "capability": capability,
                "action": target_action,
                "timestamp": time.time(),
                "policy_decision": "autonomous_authorization",
                "confidence": 1.0,
            },
        }

        provenance = self.create_provenance_record(
            capability=capability,
            entity_id=entity_id,
            action=target_action,
            decision=authorization["decision"],
            requires_human=False,
            confidence=authorization["confidence"],
            verified=True,
        )

        return {
            "allowed": True,
            "requires_authorization": True,
            "classification": "consequential",
            "capability": capability,
            "decision": authorization["decision"],
            "authorization": authorization,
            "provenance": provenance,
        }

    def create_provenance_record(
        self,
        *,
        capability,
        entity_id,
        action,
        decision,
        requires_human,
        confidence,
        success_count=0,
        failure_count=0,
        decision_id=None,
        approval_id=None,
        execution_id=None,
        verified=None,
        policy_version=None,
        previous_hash="GENESIS",
        timestamp=None,
    ):
        if timestamp is None:
            timestamp = time.time()

        record = {
            "provenance_id": str(uuid.uuid4()),
            "decision_id": decision_id,
            "approval_id": approval_id,
            "execution_id": execution_id,
            "capability": capability,
            "entity_id": entity_id,
            "action": action,
            "decision": decision,
            "requires_human": bool(requires_human),
            "confidence": float(confidence or 0.0),
            "success_count": int(success_count or 0),
            "failure_count": int(failure_count or 0),
            "verified": verified,
            "policy_version": policy_version or self.POLICY_VERSION,
            "previous_hash": previous_hash,
            "timestamp": float(timestamp),
        }

        canonical = json.dumps(
            record,
            sort_keys=True,
            separators=(",", ":"),
        )

        record["record_hash"] = hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()

        return record

    @staticmethod
    def verify_provenance(record):
        if not isinstance(record, dict):
            return False

        required = [
            "provenance_id",
            "capability",
            "entity_id",
            "action",
            "decision",
            "requires_human",
            "confidence",
            "success_count",
            "failure_count",
            "verified",
            "policy_version",
            "previous_hash",
            "timestamp",
            "record_hash",
        ]

        if not all(field in record for field in required):
            return False

        unsigned = {
            key: record[key]
            for key in record
            if key != "record_hash"
        }

        canonical = json.dumps(
            unsigned,
            sort_keys=True,
            separators=(",", ":"),
        )

        expected_hash = hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()

        return record.get("record_hash") == expected_hash
