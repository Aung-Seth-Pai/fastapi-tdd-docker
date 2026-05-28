# project/backend/app/config.py

from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import AnyUrl
import logging
import dotenv

dotenv.load_dotenv()
log = logging.getLogger("uvicorn")

class Settings(BaseSettings):
    """Application configuration settings."""
    app_name: str = "My App"
    environment: str = "dev"
    testing: bool = bool(0)
    database_url: AnyUrl
    # secret_key: str = "your-secret-key"

@lru_cache()
def get_settings() -> Settings:
    """Load and return the application settings."""
    try:
        settings = Settings()
        log.info(f"Settings loaded successfully: {settings}")
        return settings
    except Exception as e:
        log.error(f"Error loading settings: {e}")
        raise
