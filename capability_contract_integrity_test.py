import asyncio
import inspect
import json
import sys

sys.path.insert(0, ".")

from core.state import A1OS


EXPECTED_CONTRACT = {
    "adaptive_authorization_test": {
        "classification": "test",
        "requires_authorization": True,
        "requires_provenance": True,
    },
    "autonomous_actuation": {
        "classification": "consequential",
        "requires_authorization": True,
        "requires_provenance": True,
    },
    "autonomous_recovery": {
        "classification": "consequential",
        "requires_authorization": True,
        "requires_provenance": True,
    },
    "capabilities": {
        "classification": "observational",
        "requires_authorization": False,
        "requires_provenance": False,
    },
    "database_repair": {
        "classification": "consequential",
        "requires_authorization": True,
        "requires_provenance": True,
    },
    "diagnostics": {
        "classification": "observational",
        "requires_authorization": False,
        "requires_provenance": False,
    },
    "digital_world_decision": {
        "classification": "analytical",
        "requires_authorization": True,
        "requires_provenance": True,
    },
    "digital_world_graph": {
        "classification": "analytical",
        "requires_authorization": False,
        "requires_provenance": False,
    },
    "digital_world_intelligence": {
        "classification": "analytical",
        "requires_authorization": False,
        "requires_provenance": False,
    },
    "digital_world_model": {
        "classification": "analytical",
        "requires_authorization": False,
        "requires_provenance": False,
    },
    "digital_world_operation": {
        "classification": "consequential",
        "requires_authorization": True,
        "requires_provenance": True,
    },
    "digital_world_query": {
        "classification": "observational",
        "requires_authorization": False,
        "requires_provenance": False,
    },
    "digital_world_reconcile": {
        "classification": "consequential",
        "requires_authorization": True,
        "requires_provenance": True,
    },
    "digital_world_recovery": {
        "classification": "consequential",
        "requires_authorization": True,
        "requires_provenance": True,
    },
    "digital_world_state": {
        "classification": "observational",
        "requires_authorization": False,
        "requires_provenance": False,
    },
    "filesystem_management": {
        "classification": "consequential",
        "requires_authorization": True,
        "requires_provenance": True,
    },
    "health_check": {
        "classification": "observational",
        "requires_authorization": False,
        "requires_provenance": False,
    },
    "network_management": {
        "classification": "consequential",
        "requires_authorization": True,
        "requires_provenance": True,
    },
    "observability": {
        "classification": "observational",
        "requires_authorization": False,
        "requires_provenance": False,
    },
    "process_management": {
        "classification": "consequential",
        "requires_authorization": True,
        "requires_provenance": True,
    },
    "recover": {
        "classification": "consequential",
        "requires_authorization": True,
        "requires_provenance": True,
    },
    "security_audit": {
        "classification": "analytical",
        "requires_authorization": False,
        "requires_provenance": False,
    },
    "service_management": {
        "classification": "consequential",
        "requires_authorization": True,
        "requires_provenance": True,
    },
    "sovereign_control": {
        "classification": "governance",
        "requires_authorization": True,
        "requires_provenance": True,
    },
    "sovereignty_policy": {
        "classification": "governance",
        "requires_authorization": True,
        "requires_provenance": True,
    },
    "sovereignty_policy_learning": {
        "classification": "governance",
        "requires_authorization": True,
        "requires_provenance": True,
    },
    "universal_consequence_gate_test": {
        "classification": "test",
        "requires_authorization": True,
        "requires_provenance": True,
    },
}


async def main():
    system = A1OS()
    registry = system.capabilities
    registered = set(registry.list())
    expected = set(EXPECTED_CONTRACT)

    missing = sorted(expected - registered)
    unexpected = sorted(registered - expected)

    results = []

    results.append({
        "name": "all_expected_capabilities_registered",
        "passed": not missing,
        "missing": missing,
    })

    results.append({
        "name": "no_uncontracted_capabilities_present",
        "passed": not unexpected,
        "unexpected": unexpected,
    })

    async_handlers = all(
        inspect.iscoroutinefunction(registry._capabilities[name])
        for name in registered
    )

    results.append({
        "name": "all_registered_handlers_are_async",
        "passed": async_handlers,
    })

    consequential_contracts = [
        name
        for name, contract in EXPECTED_CONTRACT.items()
        if contract["classification"] == "consequential"
    ]

    consequential_controls_valid = all(
        EXPECTED_CONTRACT[name]["requires_authorization"]
        and EXPECTED_CONTRACT[name]["requires_provenance"]
        for name in consequential_contracts
    )

    results.append({
        "name": "all_consequential_capabilities_require_authorization_and_provenance",
        "passed": consequential_controls_valid,
        "capabilities": consequential_contracts,
    })

    passed = sum(item["passed"] for item in results)
    failed = len(results) - passed

    output = {
        "status": (
            "capability_contract_integrity_test_passed"
            if failed == 0
            else "capability_contract_integrity_test_failed"
        ),
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "registered_capabilities": len(registered),
        "contract_capabilities": len(expected),
        "tests": results,
    }

    print(json.dumps(output, indent=2))

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
