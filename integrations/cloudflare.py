from sdk.plugin_sdk import PluginSDK

class CloudflarePlugin(PluginSDK):
    def __init__(self, api_token):
        self.api_token = api_token

    def purge_cache(self, zone_id):
        import requests
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache"
        headers = {"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"}
        return requests.post(url, headers=headers, json={"purge_everything": True}).json()
