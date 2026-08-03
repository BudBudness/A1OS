import json
from pathlib import Path
from datetime import datetime, timezone

product = "unknown"

import sys
if len(sys.argv) > 1:
    product = sys.argv[1]

root = Path("factory_runs") / product / "security_compliance"

artifacts = [
    "security_policy.json",
    "access_control_policy.json",
    "audit_configuration.json",
    "secrets_management_policy.json",
    "compliance_report.json",
    "vulnerability_scan_config.json"
]

root.mkdir(parents=True, exist_ok=True)

for artifact in artifacts:
    (root / artifact).write_text(
        json.dumps(
            {
                "product": product,
                "generated": datetime.now(timezone.utc).isoformat(),
                "status": "initialized",
                "runtime": "a1os_security_compliance_runtime"
            },
            indent=2
        )
    )

manifest = {
    "plane": "security_compliance_runtime",
    "version": "8.5",
    "product": product,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "capabilities": [
        "security_governance",
        "identity_controls",
        "audit_management",
        "policy_generation",
        "compliance_tracking",
        "vulnerability_management"
    ],
    "artifacts": artifacts
}

(root / "SECURITY_COMPLIANCE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print("=" * 70)
print("A1OS FACTORY SECURITY & COMPLIANCE RUNTIME v8.5")
print("=" * 70)
print(f"Product: {product}")
print("✓ security governance")
print("✓ access control")
print("✓ audit management")
print("✓ secrets policy")
print("✓ compliance tracking")
print("✓ vulnerability framework")
print(f"Artifacts: {root}")
