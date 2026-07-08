"""Runtime settings loaded from environment variables."""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

from src.config.constants import APP_ROOT, TOOLKIT_ROOT

load_dotenv(APP_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    app_env: str
    ai_provider: str
    openai_api_key: str
    anthropic_api_key: str
    gemini_api_key: str
    default_data_source: str

    @property
    def data_source_path(self) -> Path:
        path = Path(self.default_data_source)
        if not path.is_absolute():
            path = APP_ROOT / path
        if path.exists():
            return path
        fallback_xlsx = APP_ROOT / "data" / "raw" / "Inventory_IT_Asset_Control_Toolkit.xlsx"
        if fallback_xlsx.exists():
            return fallback_xlsx
        toolkit_xlsx = TOOLKIT_ROOT / "dist" / "Inventory_IT_Asset_Control_Toolkit.xlsx"
        if toolkit_xlsx.exists():
            return toolkit_xlsx
        return APP_ROOT / "data" / "sample" / "sample_inventory.csv"

    @property
    def is_demo_mode(self) -> bool:
        return self.ai_provider == "local"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        ai_provider=os.getenv("AI_PROVIDER", "local"),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        default_data_source=os.getenv(
            "DEFAULT_DATA_SOURCE",
            "data/raw/Inventory_IT_Asset_Control_Toolkit.xlsx",
        ),
    )
