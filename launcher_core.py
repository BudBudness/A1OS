import os, json
from control_plane.control_plane import ControlPlane
from control_plane.persistence_manager import PersistenceManager
from control_plane.event_bus import EventBus
from control_plane.secrets_manager import SecretsManager
from control_plane.capability_contract import CapabilityContract
from generators.runtime.app_runtime import AppRuntimeEngine

class A1OSKernel:
    def __init__(self):
        self.db = PersistenceManager()
        self.bus = EventBus()
        self.vault = SecretsManager()
        self.contracts = CapabilityContract()
        self.control_plane = ControlPlane(self.db, self.bus, self.vault, self.contracts)
        self.runtime = AppRuntimeEngine(os.getcwd(), self.control_plane)
        self.departments = {}
        self.discover_departments()

    def discover_departments(self):
        modules_dir = "generators/modules"
        if not os.path.exists(modules_dir): return
        
        for folder in os.listdir(modules_dir):
            manifest_path = os.path.join(modules_dir, folder, "manifest.json")
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)
                        if 'app_id' in manifest:
                            self.departments[manifest['app_id']] = manifest
                            print(f"🚀 [DISCOVERY] Loaded department: {manifest['name']}")
                        else:
                            print(f"⚠️ [DISCOVERY] Skipping {folder}: Missing 'app_id'")
                except json.JSONDecodeError:
                    print(f"❌ [DISCOVERY] Skipping {folder}: Invalid JSON")

    def approve_intent(self, req_id):
        return self.runtime.approvals.approve(req_id)
