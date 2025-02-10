from functools import lru_cache
import os
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
    
    # API Keys (optional in test environment)
    NEXT_PUBLIC_SUPABASE_URL: Optional[str] = None
    NEXT_PUBLIC_SUPABASE_ANON_KEY: Optional[str] = None
    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    NEXT_PUBLIC_OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Firebase Configuration (optional in test environment)
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    NEXT_PUBLIC_FIREBASE_API_KEY: Optional[str] = None
    NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: Optional[str] = None
    NEXT_PUBLIC_FIREBASE_PROJECT_ID: Optional[str] = None
    NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET: Optional[str] = None
    NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID: Optional[str] = None
    NEXT_PUBLIC_FIREBASE_APP_ID: Optional[str] = None
    NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID: Optional[str] = None
    NEXT_PUBLIC_FIREBASE_VAPID_KEY: Optional[str] = None
    
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
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"  # Allow extra fields from environment variables
    )

    @property
    def is_test(self) -> bool:
        """Check if we are in test environment."""
        return self.ENVIRONMENT == "test"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache to avoid reading the .env file for every settings access
    """
    return Settings()


# Create a global settings instance
settings = get_settings() 