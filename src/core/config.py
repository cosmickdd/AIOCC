from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment or .env via pydantic."""

    COMPOSIO_API_KEY: str | None = Field(default=None, env="COMPOSIO_API_KEY")
    SLACK_BOT_TOKEN: str | None = Field(default=None, env="SLACK_BOT_TOKEN")
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///data/tasks.db", env="DATABASE_URL")
    DEBUG: bool = Field(default=False, env="DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
