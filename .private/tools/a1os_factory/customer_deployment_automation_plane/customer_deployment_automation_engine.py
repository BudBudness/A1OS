import json
import sys
from pathlib import Path
from datetime import datetime, timezone

if len(sys.argv) < 2:
    print("Usage: python3 customer_deployment_automation_engine.py product-name")
    sys.exit(1)

product = sys.argv[1]

root = Path("products") / product / "customer_deployment"

folders = [
    "tenants",
    "environments",
    "provisioning",
    "configuration",
    "database_initialization",
    "identity_setup",
    "security_baselines",
    "monitoring_activation",
    "onboarding",
    "deployment_packages",
    "automation_logs"
]

for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

manifest = {
    "product": product,
    "plane": "customer_deployment_automation",
    "version": "6.2",
    "generated": datetime.now(timezone.utc).isoformat(),
    "status": "customer_deployment_ready",
    "capabilities": [
        "tenant_provisioning",
        "environment_generation",
        "configuration_automation",
        "database_bootstrap",
        "identity_initialization",
        "security_activation",
        "monitoring_enablement",
        "customer_onboarding",
        "deployment_audit"
    ]
}

(root / "CUSTOMER_DEPLOYMENT_AUTOMATION_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2)
)

print(f"A1OS Customer Deployment Automation Plane Generated: {product}")
