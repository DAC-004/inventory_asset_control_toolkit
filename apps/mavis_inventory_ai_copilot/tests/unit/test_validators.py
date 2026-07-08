"""Unit tests for data validation."""

import pandas as pd

from src.data.validators import validate_inventory_data


def test_missing_required_columns_returns_error():
    df = pd.DataFrame({"sku": ["A"]})
    result = validate_inventory_data(df)
    assert result.is_valid is False
    assert any("Missing required columns" in e for e in result.errors)


def test_negative_inventory_qty_returns_error(normalized_sample_df):
    df = normalized_sample_df.copy()
    df.loc[0, "on_hand_qty"] = -1
    result = validate_inventory_data(df)
    assert result.is_valid is False


def test_null_sku_returns_error(normalized_sample_df):
    df = normalized_sample_df.copy()
    df.loc[0, "sku"] = ""
    result = validate_inventory_data(df)
    assert result.is_valid is False


def test_duplicate_sku_location_returns_warning(normalized_sample_df):
    df = normalized_sample_df.copy()
    dup = df.iloc[0].copy()
    df = pd.concat([df, pd.DataFrame([dup])], ignore_index=True)
    result = validate_inventory_data(df)
    assert any("Duplicate SKU-location" in w for w in result.warnings)


def test_retail_price_below_cost_returns_warning(normalized_sample_df):
    df = normalized_sample_df.copy()
    df.loc[0, "retail_price"] = 1.0
    df.loc[0, "unit_cost"] = 100.0
    result = validate_inventory_data(df)
    assert any("Retail price below unit cost" in w for w in result.warnings)


def test_max_stock_below_min_stock_returns_warning(normalized_sample_df):
    df = normalized_sample_df.copy()
    df.loc[0, "max_stock"] = 1
    df.loc[0, "min_stock"] = 50
    result = validate_inventory_data(df)
    assert any("Max stock below min stock" in w for w in result.warnings)
