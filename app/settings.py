import os
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "AI Agent Runtime")
    app_version: str = os.getenv("APP_VERSION", "2.0.0")
    app_env: str = os.getenv("APP_ENV", "production")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    log_level: str = os.getenv("LOG_LEVEL", "info")
    allowed_origins_raw: str = os.getenv("ALLOWED_ORIGINS", "*")

    @property
    def allowed_origins(self) -> List[str]:
        values = [item.strip() for item in self.allowed_origins_raw.split(",")]
        return [item for item in values if item]


settings = Settings()

