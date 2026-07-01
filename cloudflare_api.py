import requests
import os

def purge_cache(zone_id, api_token):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    data = {"purge_everything": True}
    response = requests.post(url, headers=headers, json=data)
    return response.json()
