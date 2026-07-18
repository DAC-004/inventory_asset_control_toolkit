"""Tests for fictional inventory data generation."""

import pandas as pd

from config.workbook_config import INVENTORY_STATUSES
from src.data_generation.generate_inventory import (
    COLUMN_ORDER,
    generate_inventory_data,
    save_inventory_data,
)


def test_generate_inventory_returns_dataframe():
    df = generate_inventory_data(row_count=120, seed=42)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 120


def test_inventory_columns_defined():
    df = generate_inventory_data(row_count=50, seed=42)
    assert list(df.columns) == COLUMN_ORDER
    assert "item_id" in df.columns
    assert "status" in df.columns
    assert "recommended_action" in df.columns


def test_inventory_all_statuses_represented():
    df = generate_inventory_data(row_count=120, seed=42)
    assert set(INVENTORY_STATUSES).issubset(set(df["status"]))


def test_inventory_unique_item_ids():
    df = generate_inventory_data(row_count=120, seed=42)
    assert df["item_id"].is_unique


def test_inventory_total_value_calculation():
    df = generate_inventory_data(row_count=50, seed=42)
    expected = (df["quantity_on_hand"] * df["unit_cost"]).round(2)
    pd.testing.assert_series_equal(df["total_value"], expected, check_names=False)


def test_inventory_product_names_exclude_mavis():
    df = generate_inventory_data(row_count=120, seed=42)
    combined = " ".join(df["product_name"].astype(str).tolist())
    assert "Mavis" not in combined


def test_save_inventory_data_writes_csv(tmp_path):
    df = generate_inventory_data(row_count=10, seed=42)
    path = save_inventory_data(df, output_dir=tmp_path)
    assert path.exists()
    loaded = pd.read_csv(path)
    assert len(loaded) == 10
