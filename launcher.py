import json
import os
import logging

log_path = os.path.expanduser('~/A1OS/logs/kernel.log')
logging.basicConfig(level=logging.INFO, filename=log_path)

def bootstrap():
    registry_path = os.path.expanduser('~/A1OS/cfg/registry.json')
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    for category, domains in registry.items():
        for domain in domains:
            print(f"Bootstrapping [{category.upper()}]: {domain}...")
            domain_data_path = os.path.expanduser(f'~/A1OS/data/{domain}')
            os.makedirs(domain_data_path, exist_ok=True)
            with open(f"{domain_data_path}/state.json", 'w') as sf:
                json.dump({"status": "initialized", "domain": domain}, sf)

if __name__ == "__main__":
    bootstrap()
