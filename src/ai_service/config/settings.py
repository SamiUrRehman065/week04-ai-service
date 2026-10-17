import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central application settings loaded from the environment."""

    APP_NAME: str = os.getenv("APP_NAME", "Week 04 AI Service")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"


settings = Settings()
