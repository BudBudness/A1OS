import os

DEBUG = os.getenv("DEBUG", "False").lower() == "true"
API_PORT = int(os.getenv("API_PORT", 8086))
PWA_PORT = int(os.getenv("PWA_PORT", 8000))