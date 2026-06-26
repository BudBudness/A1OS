import os
from dataclasses import dataclass

@dataclass
class Settings:
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    API_PORT: int = int(os.getenv("API_PORT", "8086"))
    PWA_PORT: int = int(os.getenv("PWA_PORT", "8000"))
    DB_PATH: str = os.getenv("DB_PATH", "data/a1os.db")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
