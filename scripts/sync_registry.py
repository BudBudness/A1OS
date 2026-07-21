import os
import json

workers = ["crm_worker", "finance_worker", "ops_worker", "intel_worker", "governance_worker"]
data = {"workers": {w: f"modules.{w.split('_')[0]}.{w}" for w in workers}}

with open("cfg/registry.json", "w") as f:
    json.dump(data, f, indent=4)
