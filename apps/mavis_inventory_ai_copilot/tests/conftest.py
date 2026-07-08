"""Shared pytest fixtures."""

from __future__ import annotations

import pandas as pd
import pytest

from src.config.constants import APP_ROOT
from src.data.transformers import enrich_discontinued_flag, normalize_columns
from src.models.inventory import InventoryHealthRecord, InventoryRecord
from src.services.inventory_health_service import classify_inventory


@pytest.fixture
def sample_record() -> InventoryRecord:
    return InventoryRecord(
        sku="TEST-001",
        product_name="Test Product",
        category="Tires",
        location="DC-NJ",
        location_type="Distribution Center",
        region="Northeast",
        on_hand_qty=50,
        min_stock=10,
        max_stock=40,
        unit_cost=100.0,
        retail_price=150.0,
        inventory_age_days=200,
        demand_90_day=10,
        avg_weekly_sales=5.0,
        discontinued_flag=False,
        transfer_cost_per_unit=2.5,
    )


@pytest.fixture
def sample_health_records() -> list[InventoryHealthRecord]:
    records = [
        InventoryRecord(
            sku="TR-001",
            product_name="Transfer Source",
            category="Tires",
            location="DC-NJ",
            location_type="Distribution Center",
            region="Northeast",
            on_hand_qty=80,
            min_stock=10,
            max_stock=40,
            unit_cost=100.0,
            retail_price=150.0,
            inventory_age_days=200,
            demand_90_day=5,
            avg_weekly_sales=2.0,
            discontinued_flag=False,
            transfer_cost_per_unit=2.5,
        ),
        InventoryRecord(
            sku="TR-001",
            product_name="Transfer Source",
            category="Tires",
            location="Store-Bronx",
            location_type="Retail Store",
            region="NYC Metro",
            on_hand_qty=5,
            min_stock=15,
            max_stock=45,
            unit_cost=100.0,
            retail_price=150.0,
            inventory_age_days=30,
            demand_90_day=25,
            avg_weekly_sales=8.0,
            discontinued_flag=False,
            transfer_cost_per_unit=2.5,
        ),
        InventoryRecord(
            sku="MD-001",
            product_name="Markdown Item",
            category="Brake Parts",
            location="Store-Queens",
            location_type="Retail Store",
            region="NYC Metro",
            on_hand_qty=60,
            min_stock=10,
            max_stock=35,
            unit_cost=30.0,
            retail_price=50.0,
            inventory_age_days=400,
            demand_90_day=0,
            avg_weekly_sales=0.0,
            discontinued_flag=True,
            transfer_cost_per_unit=2.5,
        ),
        InventoryRecord(
            sku="SO-001",
            product_name="Stockout Item",
            category="Filters",
            location="Store-Manhattan",
            location_type="Retail Store",
            region="NYC Metro",
            on_hand_qty=3,
            min_stock=15,
            max_stock=40,
            unit_cost=15.0,
            retail_price=25.0,
            inventory_age_days=45,
            demand_90_day=20,
            avg_weekly_sales=6.0,
            discontinued_flag=False,
            transfer_cost_per_unit=2.5,
        ),
    ]
    return classify_inventory(records)


@pytest.fixture
def sample_csv_path():
    return APP_ROOT / "data" / "sample" / "sample_inventory.csv"


@pytest.fixture
def normalized_sample_df(sample_csv_path) -> pd.DataFrame:
    df = pd.read_csv(sample_csv_path)
    df = normalize_columns(df)
    return enrich_discontinued_flag(df)
