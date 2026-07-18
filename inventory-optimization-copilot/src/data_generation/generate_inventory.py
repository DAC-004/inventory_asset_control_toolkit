"""
Generate fictional inventory records — backward-compatible entry point.

Full multi-dataset generation lives in ``pipeline.py``.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from config.workbook_config import (
    CSV_FILES,
    DATA_GENERATED_DIR,
    RANDOM_SEED,
    ROW_COUNTS,
)
from src.data_generation.pipeline import generate_all_datasets, generate_inventory
from src.domain.rng import SeededRNG
from src.services.workbook_inventory import COLUMN_ORDER  # noqa: F401 — re-export

# Re-export catalog for tests
from src.domain.catalog import LOCATIONS, PRODUCT_CATALOG  # noqa: F401


def generate_inventory_data(
    row_count: int | None = None,
    seed: int | None = None,
) -> pd.DataFrame:
    """Build inventory DataFrame (SKU + location grain)."""
    rng = SeededRNG.create(seed)
    return generate_inventory(rng, row_count=row_count)


def save_inventory_data(df: pd.DataFrame, output_dir: Path | None = None) -> Path:
    """Write inventory data to CSV in data/generated/."""
    output_dir = output_dir or DATA_GENERATED_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / CSV_FILES["inventory"]
    df.to_csv(path, index=False, date_format="%Y-%m-%d")
    return path


def generate_and_save_all(
    seed: int | None = None,
    row_count: int | None = None,
    output_dir: Path | None = None,
) -> dict[str, pd.DataFrame]:
    """Generate all datasets, validate, and save CSVs."""
    from src.data_generation.pipeline import save_all_datasets

    seed = seed if seed is not None else RANDOM_SEED
    row_count = row_count or ROW_COUNTS["inventory"]["default"]
    datasets = generate_all_datasets(seed=seed, row_count=row_count, validate=True)
    save_all_datasets(datasets, output_dir=output_dir)
    return datasets
