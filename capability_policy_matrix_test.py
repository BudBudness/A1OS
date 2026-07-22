import json
import sys

sys.path.insert(0, ".")

from core.state import A1OS


POLICY_MATRIX = {
    "adaptive_authorization_test": {
        "lifecycle": "test",
        "classification": "test",
        "allowed_actions": ["test"],
        "requires_authorization": True,
        "requires_provenance": True,
        "requires_verification": True,
    },
    "autonomous_actuation": {
        "lifecycle": "operational",
        "classification": "consequential",
        "allowed_actions": ["actuate"],
        "requires_authorization": True,
        "requires_provenance": True,
        "requires_verification": True,
    },
    "autonomous_recovery": {
        "lifecycle": "operational",
        "classification": "consequential",
        "allowed_actions": ["recover"],
        "requires_authorization": True,
        "requires_provenance": True,
        "requires_verification": True,
    },
    "capabilities": {
        "lifecycle": "system",
        "classification": "observational",
        "allowed_actions": ["list"],
        "requires_authorization": False,
        "requires_provenance": False,
        "requires_verification": False,
    },
    "database_repair": {
        "lifecycle": "operational",
        "classification": "consequential",
        "allowed_actions": ["repair"],
        "requires_authorization": True,
        "requires_provenance": True,
        "requires_verification": True,
    },
    "diagnostics": {
        "lifecycle": "observational",
        "classification": "observational",
        "allowed_actions": ["diagnose"],
        "requires_authorization": False,
        "requires_provenance": False,
        "requires_verification": False,
    },
    "digital_world_decision": {
        "lifecycle": "analytical",
        "classification": "analytical",
        "allowed_actions": ["decide"],
        "requires_authorization": True,
        "requires_provenance": True,
        "requires_verification": True,
    },
    "digital_world_graph": {
        "lifecycle": "analytical",
        "classification": "analytical",
        "allowed_actions": ["graph"],
        "requires_authorization": False,
        "requires_provenance": False,
        "requires_verification": False,
    },
    "digital_world_intelligence": {
        "lifecycle": "analytical",
        "classification": "analytical",
        "allowed_actions": ["analyze"],
        "requires_authorization": False,
        "requires_provenance": False,
        "requires_verification": False,
    },
    "digital_world_model": {
        "lifecycle": "analytical",
        "classification": "analytical",
        "allowed_actions": ["model"],
        "requires_authorization": False,
        "requires_provenance": False,
        "requires_verification": False,
    },
    "digital_world_operation": {
        "lifecycle": "operational",
        "classification": "consequential",
        "allowed_actions": ["operate"],
        "requires_authorization": True,
        "requires_provenance": True,
        "requires_verification": True,
    },
    "digital_world_query": {
        "lifecycle": "observational",
        "classification": "observational",
        "allowed_actions": ["query"],
        "requires_authorization": False,
        "requires_provenance": False,
        "requires_verification": False,
    },
    "digital_world_reconcile": {
        "lifecycle": "operational",
        "classification": "consequential",
        "allowed_actions": ["reconcile"],
        "requires_authorization": True,
        "requires_provenance": True,
        "requires_verification": True,
    },
    "digital_world_recovery": {
        "lifecycle": "operational",
        "classification": "consequential",
        "allowed_actions": ["recover", "repair"],
        "requires_authorization": True,
        "requires_provenance": True,
        "requires_verification": True,
    },
    "digital_world_state": {
        "lifecycle": "observational",
        "classification": "observational",
        "allowed_actions": ["read"],
        "requires_authorization": False,
        "requires_provenance": False,
        "requires_verification": False,
    },
    "filesystem_management": {
        "lifecycle": "operational",
        "classification": "consequential",
        "allowed_actions": ["read", "write", "delete"],
        "requires_authorization": True,
        "requires_provenance": True,
        "requires_verification": True,
    },
    "health_check": {
        "lifecycle": "observational",
        "classification": "observational",
        "allowed_actions": ["health"],
        "requires_authorization": False,
        "requires_provenance": False,
        "requires_verification": False,
    },
    "network_management": {
        "lifecycle": "operational",
        "classification": "consequential",
        "allowed_actions": ["configure", "repair"],
        "requires_authorization": True,
        "requires_provenance": True,
        "requires_verification": True,
    },
    "observability": {
        "lifecycle": "observational",
        "classification": "observational",
        "allowed_actions": ["observe"],
        "requires_authorization": False,
        "requires_provenance": False,
        "requires_verification": False,
    },
    "process_management": {
        "lifecycle": "operational",
        "classification": "consequential",
        "allowed_actions": ["start", "stop", "restart"],
        "requires_authorization": True,
        "requires_provenance": True,
        "requires_verification": True,
    },
    "recover": {
        "lifecycle": "operational",
        "classification": "consequential",
        "allowed_actions": ["recover"],
        "requires_authorization": True,
        "requires_provenance": True,
        "requires_verification": True,
    },
    "security_audit": {
        "lifecycle": "analytical",
        "classification": "analytical",
        "allowed_actions": ["audit"],
        "requires_authorization": False,
        "requires_provenance": False,
        "requires_verification": False,
    },
    "service_management": {
        "lifecycle": "operational",
        "classification": "consequential",
        "allowed_actions": ["start", "stop", "restart", "deploy"],
        "requires_authorization": True,
        "requires_provenance": True,
        "requires_verification": True,
    },
    "sovereign_control": {
        "lifecycle": "governance",
        "classification": "governance",
        "allowed_actions": ["control"],
        "requires_authorization": True,
        "requires_provenance": True,
        "requires_verification": True,
    },
    "sovereignty_policy": {
        "lifecycle": "governance",
        "classification": "governance",
        "allowed_actions": ["authorize", "deny"],
        "requires_authorization": True,
        "requires_provenance": True,
        "requires_verification": True,
    },
    "sovereignty_policy_learning": {
        "lifecycle": "governance",
        "classification": "governance",
        "allowed_actions": ["learn"],
        "requires_authorization": True,
        "requires_provenance": True,
        "requires_verification": True,
    },
    "universal_consequence_gate_test": {
        "lifecycle": "test",
        "classification": "test",
        "allowed_actions": ["test"],
        "requires_authorization": True,
        "requires_provenance": True,
        "requires_verification": True,
    },
}


def main():
    system = A1OS()
    registered = set(system.capabilities.list())
    contracted = set(POLICY_MATRIX)

    results = []

    missing = sorted(contracted - registered)
    unexpected = sorted(registered - contracted)

    results.append({
        "name": "policy_matrix_covers_all_registered_capabilities",
        "passed": not missing,
        "missing": missing,
    })

    results.append({
        "name": "policy_matrix_contains_no_unregistered_capabilities",
        "passed": not unexpected,
        "unexpected": unexpected,
    })

    invalid_entries = []

    for capability, policy in POLICY_MATRIX.items():
        required = {
            "lifecycle",
            "classification",
            "allowed_actions",
            "requires_authorization",
            "requires_provenance",
            "requires_verification",
        }

        missing_fields = sorted(required - set(policy))

        if missing_fields:
            invalid_entries.append({
                "capability": capability,
                "missing_fields": missing_fields,
            })

    results.append({
        "name": "every_capability_has_complete_policy_contract",
        "passed": not invalid_entries,
        "invalid_entries": invalid_entries,
    })

    consequential_without_controls = [
        capability
        for capability, policy in POLICY_MATRIX.items()
        if policy["classification"] == "consequential"
        and not (
            policy["requires_authorization"]
            and policy["requires_provenance"]
            and policy["requires_verification"]
        )
    ]

    results.append({
        "name": "consequential_capabilities_have_full_control_chain",
        "passed": not consequential_without_controls,
        "invalid_capabilities": consequential_without_controls,
    })

    governance_without_controls = [
        capability
        for capability, policy in POLICY_MATRIX.items()
        if policy["classification"] == "governance"
        and not (
            policy["requires_authorization"]
            and policy["requires_provenance"]
            and policy["requires_verification"]
        )
    ]

    results.append({
        "name": "governance_capabilities_have_full_control_chain",
        "passed": not governance_without_controls,
        "invalid_capabilities": governance_without_controls,
    })

    passed = sum(item["passed"] for item in results)
    failed = len(results) - passed

    output = {
        "status": (
            "capability_policy_matrix_test_passed"
            if failed == 0
            else "capability_policy_matrix_test_failed"
        ),
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "registered_capabilities": len(registered),
        "policy_entries": len(POLICY_MATRIX),
        "tests": results,
    }

    print(json.dumps(output, indent=2))

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
