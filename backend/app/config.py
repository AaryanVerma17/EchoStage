from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    decider_url: str = "http://127.0.0.1:8099"
    decider_model: str = "StrandsAgents/strands-decider-2B-qwen3.5-v1-2610"
    decider_mode: str = "live"
    confidence_threshold: float = 0.60
    request_timeout_seconds: float = 30.0
    cors_origins: str = "http://localhost:5173"
    event_log_path: str = "./data/events.jsonl"
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "amazon.nova-lite-v1:0"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins(self):
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings():
    return Settings()
