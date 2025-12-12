from __future__ import annotations

from functools import lru_cache

from pydantic import HttpUrl, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="")

    bot_token: str
    admin_chat_id: int
    api_base_url: HttpUrl
    internal_bot_token: str
    internal_leafflow_token: str
    webapp_url: HttpUrl
    webhook_secret: str
    webhook_base_url: HttpUrl = "http://localhost:8000"

    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    webhook_path: str = "/telegram/webhook"

    @computed_field
    @property
    def webhook_url(self) -> str:
        return f"{str(self.webhook_base_url).rstrip('/')}{self.webhook_path}?secret_token={self.webhook_secret}"


@lru_cache(maxsize=1)
def load_settings() -> Settings:
    return Settings()
