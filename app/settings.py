from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    FIREBASE_DEBUG: str = "0"
    CORS_ORIGINS: str = ""
    JWT_SECRET_KEY: str = "change-me"

    @property
    def is_debug_mode(self) -> bool:
        return str(self.FIREBASE_DEBUG).strip() == "1"

    @property
    def cors_origins_list(self) -> List[str]:
        raw = (self.CORS_ORIGINS or "").strip()
        if raw:
            return [o.strip() for o in raw.split(",") if o.strip()]
        return [
            "https://www.titletesterpro.com",
            "https://titletesterpro.com",
            "https://*.vercel.app",
            "http://localhost:5173",
        ]

settings = Settings()
