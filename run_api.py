import os
from cloudflare_api import purge_cache

ZONE_ID = "11bcb4d4054ce1d6adf17f50b4c88637"
API_TOKEN = os.getenv("CF_API_TOKEN")

if not API_TOKEN:
    print("Error: CF_API_TOKEN environment variable not set.")
else:
    result = purge_cache(ZONE_ID, API_TOKEN)
    print(result)
