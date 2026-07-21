from typing import Dict, Type
from archive.apps.base import BaseApp

class MarketplaceRegistry:
    def __init__(self):
        self.available_apps: Dict[str, Type[BaseApp]] = {}
        self.installed_apps: Dict[str, BaseApp] = {}

    def publish_to_marketplace(self, app_id: str, app_class: Type[BaseApp]):
        self.available_apps[app_id] = app_class

    def install_app(self, app_id: str, runtime) -> bool:
        if app_id in self.available_apps and app_id not in self.installed_apps:
            instance = self.available_apps[app_id]()
            self.installed_apps[app_id] = instance
            runtime.register_app(app_id, instance)
            return True
        return False

