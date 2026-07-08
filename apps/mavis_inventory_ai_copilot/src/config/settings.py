"""Runtime settings loaded from environment variables."""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from src.config.constants import APP_ROOT, REPO_ROOT, TOOLKIT_ROOT
from src.config.runtime import is_browser_runtime

BROWSER_DATA_SOURCE = "data/sample/sample_inventory.csv"


def _load_env_files() -> None:
    if is_browser_runtime():
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(APP_ROOT / ".env")
    load_dotenv(APP_ROOT / ".env.local", override=True)
    load_dotenv(REPO_ROOT / ".env.local", override=True)


_load_env_files()


@dataclass(frozen=True)
class Settings:
    app_env: str
    ai_provider: str
    openai_api_key: str
    openai_model: str
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
        if is_browser_runtime():
            browser_csv = APP_ROOT / BROWSER_DATA_SOURCE
            if browser_csv.exists():
                return browser_csv
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

    @property
    def uses_openai_proxy(self) -> bool:
        return is_browser_runtime() and self.ai_provider == "openai"


@lru_cache
def get_settings() -> Settings:
    default_data_source = os.getenv("DEFAULT_DATA_SOURCE")
    if default_data_source is None and is_browser_runtime():
        default_data_source = BROWSER_DATA_SOURCE

    default_provider = "openai" if is_browser_runtime() else "openai"

    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        ai_provider=os.getenv("AI_PROVIDER", default_provider),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        default_data_source=default_data_source
        or "data/raw/Inventory_IT_Asset_Control_Toolkit.xlsx",
    )
