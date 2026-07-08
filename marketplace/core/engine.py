from typing import Dict, List
import uuid

class MarketplaceEngine:
    def __init__(self):
        self.apps: Dict[str, Dict] = {}
        self.listings: List[Dict] = []
        self.purchases: Dict[str, Dict] = {}
    
    def publish_app(self, name: str, version: str, manifest: Dict) -> str:
        app_id = str(uuid.uuid4())
        self.apps[app_id] = {
            "id": app_id,
            "name": name,
            "version": version,
            "manifest": manifest,
            "published": "now"
        }
        return app_id
    
    def install_app(self, app_id: str, tenant_id: str) -> bool:
        if app_id not in self.apps:
            return False
        self.purchases[tenant_id] = {
            "app_id": app_id,
            "installed": "now"
        }
        return True
    
    def list_apps(self) -> List[Dict]:
        return list(self.apps.values())
