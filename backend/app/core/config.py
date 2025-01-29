from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Settings
    ENVIRONMENT: str = "development"
    
    # JWT Settings
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30
    
    # Slack Settings
    SLACK_API_TOKEN: Optional[str] = None
    
    # Add validation for Slack token
    @property
    def is_slack_configured(self) -> bool:
        return bool(self.SLACK_API_TOKEN and self.SLACK_API_TOKEN.startswith("xoxb-"))
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache to avoid reading the .env file for every settings access
    """
    return Settings()


# Create a global settings instance
settings = get_settings() 