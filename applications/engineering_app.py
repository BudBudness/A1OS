from applications.base_app import BaseApplication
from integrations.cloudflare import CloudflarePlugin
from sdk.worker_sdk import WorkerSDK
from system.config import ConfigManager

class EngineeringApp(BaseApplication):
    def __init__(self):
        self.config = ConfigManager()
        token = self.config.get("cloudflare_token")
        
        super().__init__(
            name="Engineering Infrastructure Manager",
            description="Manages cloud infrastructure via A1OS plugins.",
            required_plugins=["cloudflare"]
        )
        self.cf = CloudflarePlugin(api_token=token)
        self.worker = WorkerSDK("InfraBot", "Infrastructure Manager", "Engineering")

    def run_purge(self, zone_id):
        action = lambda: self.cf.purge_cache(zone_id)
        return self.worker.perform_task("Purge Cloudflare Cache", action)

    def run(self, zone_id):
        if self.validate_environment():
            return self.run_purge(zone_id)
