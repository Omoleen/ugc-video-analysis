"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars like NGROK_AUTHTOKEN
    )

    # Slack Configuration
    slack_bot_token: str
    slack_signing_secret: str

    # Channel IDs
    video_review_channel: str
    approved_content_channel: str

    # Gemini Configuration
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash"

    # Application Settings
    score_threshold: int = 80

    # Database Configuration
    # For local dev: leave empty (uses SQLite)
    # For production: postgresql+asyncpg://user:pass@host:port/dbname
    database_url: str | None = None


settings = Settings()
