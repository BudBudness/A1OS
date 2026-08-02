from pathlib import Path
import yaml
import json
import sys

ROOT = Path("products")
DNA = Path("tools/a1os_factory/dna/product_profiles.yaml")

if len(sys.argv) < 3:
    print("Usage: python3 dna_engine.py <product-name> <profile>")
    sys.exit(1)

name = sys.argv[1]
profile = sys.argv[2]

profiles = yaml.safe_load(
    DNA.read_text()
)["profiles"]

if profile not in profiles:
    print("Unknown profile")
    sys.exit(1)

definition = profiles[profile]

product = ROOT / name

for layer in definition["layers"]:
    (product / layer).mkdir(
        parents=True,
        exist_ok=True
    )

for module in definition["modules"]:
    (product / "core" / module).mkdir(
        parents=True,
        exist_ok=True
    )

metadata = {
    "product": name,
    "dna_profile": profile,
    "layers": definition["layers"],
    "modules": definition["modules"],
    "factory": "A1OS Product DNA Engine v1.2"
}

(product / "A1OS_DNA.json").write_text(
    json.dumps(metadata, indent=2)
)

print(
    f"A1OS DNA generated: {name} ({profile})"
)
