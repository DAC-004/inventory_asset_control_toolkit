"""Integration tests for Excel loading."""

from pathlib import Path

import pytest

from src.config.constants import APP_ROOT, TOOLKIT_ROOT
from src.data.loaders import load_inventory_data
from src.data.transformers import normalize_columns


@pytest.fixture
def workbook_path() -> Path | None:
    candidates = [
        APP_ROOT / "data" / "raw" / "Inventory_IT_Asset_Control_Toolkit.xlsx",
        TOOLKIT_ROOT / "dist" / "Inventory_IT_Asset_Control_Toolkit.xlsx",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def test_excel_workbook_loads(workbook_path):
    if workbook_path is None:
        pytest.skip("Workbook not available")
    df = load_inventory_data(workbook_path)
    assert len(df) > 0


def test_excel_columns_normalize(workbook_path):
    if workbook_path is None:
        pytest.skip("Workbook not available")
    df = normalize_columns(load_inventory_data(workbook_path))
    assert "sku" in df.columns
    assert "on_hand_qty" in df.columns
