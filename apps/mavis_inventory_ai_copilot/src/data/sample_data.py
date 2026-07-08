"""Fallback sample inventory dataset generator."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config.constants import APP_ROOT
from src.data.loaders import load_inventory_data


def get_sample_inventory_path() -> Path:
    return APP_ROOT / "data" / "sample" / "sample_inventory.csv"


def load_sample_inventory() -> pd.DataFrame:
    """Load bundled sample inventory CSV."""
    path = get_sample_inventory_path()
    if path.exists():
        return load_inventory_data(path)
    return _generate_minimal_sample()


def _generate_minimal_sample() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "sku": "DEMO-001",
                "product_name": "Demo Tire 205/55R16",
                "category": "Tires",
                "location": "DC-NJ",
                "location_type": "Distribution Center",
                "region": "Northeast",
                "quantity_on_hand": 80,
                "min_stock": 10,
                "max_stock": 40,
                "unit_cost": 95.0,
                "selling_price": 140.0,
                "age_days": 220,
                "demand_90_day": 5,
            },
            {
                "sku": "DEMO-001",
                "product_name": "Demo Tire 205/55R16",
                "category": "Tires",
                "location": "Store-Bronx",
                "location_type": "Retail Store",
                "region": "NYC Metro",
                "quantity_on_hand": 8,
                "min_stock": 15,
                "max_stock": 45,
                "unit_cost": 95.0,
                "selling_price": 140.0,
                "age_days": 45,
                "demand_90_day": 22,
            },
        ]
    )
