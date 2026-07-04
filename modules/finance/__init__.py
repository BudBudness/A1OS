from .config_loader import ConfigLoader

class Finance:
    def refresh_metrics(self):
        return 'Finance metrics refreshed.'

    def connect_api(self, service_name):
        key = ConfigLoader.get_api_key(service_name)
        return f"Connecting to {service_name} API... Status: {'Key Found' if key != 'NOT_CONFIGURED' else 'Key Missing'}"

    def sync_assets(self):
        return "Asset synchronization active."
