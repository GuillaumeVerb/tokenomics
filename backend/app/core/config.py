from functools import lru_cache
from typing import Optional, Union, List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8501"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5000"
    
    # Flask Settings
    FLASK_ENV: str = "development"
    FLASK_APP: str = "run.py"
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # SMTP Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your_email@gmail.com"
    SMTP_PASSWORD: str = "your_app_specific_password"
    
    # JWT Settings
    JWT_SECRET: str = "your_jwt_secret_key_here"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30
    JWT_ACCESS_TOKEN_EXPIRES: int = 3600
    JWT_SECRET_KEY: str = "your_jwt_secret_key_here"
    
    # Slack Settings
    SLACK_API_TOKEN: Optional[str] = None
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    
    # Add validation for Slack token
    @property
    def is_slack_configured(self) -> bool:
        return bool(self.SLACK_API_TOKEN and self.SLACK_API_TOKEN.startswith("xoxb-"))
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "tokenomics"
    
    # CoinGecko settings
    COINGECKO_API_KEY: Union[str, None] = None  # Optional, can be None for public API
    
    # Python Path Settings
    PYTHONPATH: Optional[str] = None
    PYTHON_PATH: Optional[str] = None
    BACKEND_PATH: Optional[str] = None
    MYPYPATH: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"  # Allow extra fields from environment variables
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