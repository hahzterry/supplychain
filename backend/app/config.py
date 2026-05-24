from __future__ import annotations

from pathlib import Path

import yaml
from pydantic_settings import BaseSettings


_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

with open(_CONFIG_PATH) as f:
    _raw = yaml.safe_load(f)


class Settings(BaseSettings):
    host: str = _raw["server"]["host"]
    port: int = _raw["server"]["port"]
    cors_origins: list[str] = _raw["server"]["cors_origins"]

    ai_provider: str = _raw["ai"]["provider"]
    ai_model: str = _raw["ai"]["model"]

    data_source_type: str = _raw["data_source"]["type"]

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-5.4-mini"

    applicationinsights_connection_string: str = ""

    azure_storage_connection_string: str = ""
    azure_storage_container: str = "reports"

    app_username: str = "admin"
    app_password: str = "rashid2026"

    model_config = {"env_file": str(Path(__file__).resolve().parent.parent / ".env"), "extra": "ignore"}


settings = Settings()
