"""
Tests for fictional data generation.
"""

import pandas as pd

from config.workbook_config import INVENTORY_STATUSES
from src.data_generation.generate_disposal import (
    COLUMN_ORDER as DISPOSAL_COLUMNS,
    generate_disposal_data,
    save_disposal_data,
)
from src.data_generation.generate_inventory import (
    COLUMN_ORDER,
    generate_inventory_data,
    save_inventory_data,
)
from src.data_generation.generate_it_assets import (
    COLUMN_ORDER as IT_ASSET_COLUMNS,
    generate_it_asset_data,
    save_it_asset_data,
)
from src.data_generation.generate_mobile import (
    COLUMN_ORDER as MOBILE_COLUMNS,
    generate_mobile_data,
    save_mobile_data,
)
from src.data_generation.generate_software import (
    COLUMN_ORDER as SOFTWARE_COLUMNS,
    generate_software_data,
    save_software_data,
)


def test_generate_inventory_returns_dataframe():
    """Inventory generator should return a pandas DataFrame."""
    df = generate_inventory_data(row_count=120, seed=42)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 120


def test_inventory_columns_defined():
    """Inventory DataFrame should define all required columns in sheet order."""
    df = generate_inventory_data(row_count=50, seed=42)
    assert list(df.columns) == COLUMN_ORDER
    assert "item_id" in df.columns
    assert "status" in df.columns
    assert "recommended_action" in df.columns


def test_inventory_all_statuses_represented():
    """Dataset must include at least one row for every inventory status."""
    df = generate_inventory_data(row_count=120, seed=42)
    assert set(INVENTORY_STATUSES).issubset(set(df["status"]))


def test_inventory_unique_item_ids():
    """Item ID must be unique across all records."""
    df = generate_inventory_data(row_count=120, seed=42)
    assert df["item_id"].is_unique


def test_inventory_total_value_calculation():
    """Total Value should equal Quantity On Hand × Unit Cost."""
    df = generate_inventory_data(row_count=50, seed=42)
    expected = (df["quantity_on_hand"] * df["unit_cost"]).round(2)
    pd.testing.assert_series_equal(df["total_value"], expected, check_names=False)


def test_save_inventory_data_writes_csv(tmp_path):
    """save_inventory_data should write a CSV file to the output directory."""
    df = generate_inventory_data(row_count=10, seed=42)
    path = save_inventory_data(df, output_dir=tmp_path)
    assert path.exists()
    loaded = pd.read_csv(path)
    assert len(loaded) == 10


def test_it_assets_required_scenarios():
    """IT asset data must include assigned, in-stock, missing, retired, pending disposal."""
    df = generate_it_asset_data(row_count=120, seed=42)
    assert list(df.columns) == IT_ASSET_COLUMNS
    assert "Assigned" in df["status"].values
    assert "In Stock" in df["status"].values
    assert "Missing" in df["status"].values
    assert "Retired" in df["status"].values
    assert df["notes"].str.contains("Pending disposal", case=False).any()
    assert df["asset_tag"].is_unique


def test_software_compliance_scenarios():
    """Software data must include over-assigned and renewals at 30/60/90 days."""
    df = generate_software_data(row_count=22, seed=42)
    assert list(df.columns) == SOFTWARE_COLUMNS
    assert "Over-Assigned" in df["compliance_status"].values
    assert (df["days_until_renewal"] <= 30).any()
    assert ((df["days_until_renewal"] > 30) & (df["days_until_renewal"] <= 60)).any()
    assert (df["days_until_renewal"] == 90).any()
    expected_available = df["purchased_licenses"] - df["assigned_licenses"]
    pd.testing.assert_series_equal(
        df["available_licenses"], expected_available, check_names=False
    )


def test_mobile_provisioning_scenarios():
    """Mobile data must include pending setup and other key statuses."""
    df = generate_mobile_data(row_count=45, seed=42)
    assert list(df.columns) == MOBILE_COLUMNS
    assert "Pending Setup" in df["status"].values
    assert "Assigned" in df["status"].values
    assert "Missing Agreement" in df["status"].values
    assert df["asset_tag"].is_unique


def test_disposal_scenarios():
    """Disposal data must include pending wipe and certificate missing records."""
    df = generate_disposal_data(row_count=25, seed=42)
    assert list(df.columns) == DISPOSAL_COLUMNS
    assert "Pending Wipe" in df["disposal_status"].values
    assert "Certificate Missing" in df["disposal_status"].values
    assert "Disposed" in df["disposal_status"].values
    assert df["asset_tag"].is_unique


def test_all_generators_save_csv(tmp_path):
    """Each generator save function should write a CSV file."""
    seed = 42
    generators = [
        (generate_inventory_data, save_inventory_data, 10),
        (generate_it_asset_data, save_it_asset_data, 10),
        (generate_software_data, save_software_data, 10),
        (generate_mobile_data, save_mobile_data, 10),
        (generate_disposal_data, save_disposal_data, 10),
    ]
    for generate_fn, save_fn, count in generators:
        df = generate_fn(row_count=count, seed=seed)
        path = save_fn(df, output_dir=tmp_path)
        assert path.exists()
