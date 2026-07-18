"""Tests for full data model, validation, and CSV pipeline."""

from pathlib import Path

import pandas as pd

from config.workbook_config import CSV_FILES
from src.data_generation.pipeline import generate_all_datasets, save_all_datasets
from src.domain.schemas import ALL_DATASET_COLUMNS, REQUIRED_CSV_FILES
from src.domain.validation import (
    DatasetValidationError,
    quantity_on_order_by_sku_location,
    validate_all_datasets,
)
from src.main import generate_all_data
from src.services.workbook_inventory import inventory_for_workbook
from src.workbook.builder import build_workbook


def test_pipeline_is_deterministic():
    a = generate_all_datasets(seed=42, row_count=120, validate=True)
    b = generate_all_datasets(seed=42, row_count=120, validate=True)
    for key in a:
        pd.testing.assert_frame_equal(a[key], b[key])


def test_all_required_csv_files_defined():
    assert set(CSV_FILES.values()) == set(REQUIRED_CSV_FILES)


def test_all_datasets_have_required_columns():
    datasets = generate_all_datasets(seed=42, row_count=120, validate=True)
    for name, columns in ALL_DATASET_COLUMNS.items():
        df = datasets[name]
        if name == "inventory":
            assert list(df.columns) == columns + ["location"]
        else:
            assert list(df.columns) == columns


def test_inventory_snapshots_have_twelve_months():
    datasets = generate_all_datasets(seed=42, row_count=120, validate=True)
    snaps = datasets["inventory_snapshots"]
    assert snaps["snapshot_date"].nunique() >= 12


def test_demand_history_at_least_fifty_two_weeks():
    datasets = generate_all_datasets(seed=42, row_count=120, validate=True)
    assert len(datasets["demand_history"]) >= 52


def test_no_quantity_on_order_column_in_inventory():
    datasets = generate_all_datasets(seed=42, row_count=120, validate=True)
    assert "quantity_on_order" not in datasets["inventory"].columns


def test_quantity_on_order_derived_from_open_pos():
    datasets = generate_all_datasets(seed=42, row_count=120, validate=True)
    on_order = quantity_on_order_by_sku_location(datasets["purchase_orders"])
    assert isinstance(on_order, dict)


def test_receipt_quantities_balance():
    datasets = generate_all_datasets(seed=42, row_count=120, validate=True)
    receipts = datasets["purchase_order_receipts"]
    if not receipts.empty:
        assert (
            receipts["received_quantity"]
            == receipts["accepted_quantity"] + receipts["rejected_quantity"]
        ).all()


def test_customer_order_line_balance():
    datasets = generate_all_datasets(seed=42, row_count=120, validate=True)
    orders = datasets["customer_orders"]
    assert (
        orders["ordered_units"]
        == orders["fulfilled_units"] + orders["backordered_units"]
    ).all()


def test_cycle_count_variance_calculation():
    datasets = generate_all_datasets(seed=42, row_count=120, validate=True)
    counts = datasets["cycle_counts"]
    expected = counts["physical_quantity"] - counts["system_quantity"]
    pd.testing.assert_series_equal(
        counts["variance_units"], expected, check_names=False
    )


def test_validation_raises_on_bad_inventory():
    datasets = generate_all_datasets(seed=42, row_count=120, validate=False)
    bad = datasets["inventory"].copy()
    bad.loc[0, "total_value"] = -1.0
    datasets["inventory"] = bad
    try:
        validate_all_datasets(datasets)
        raised = False
    except DatasetValidationError as exc:
        raised = True
        assert exc.errors[0].dataset == "inventory"
        assert exc.errors[0].field == "total_value"
    assert raised


def test_save_all_datasets_writes_eight_files(tmp_path: Path):
    datasets = generate_all_datasets(seed=42, row_count=80, validate=True)
    paths = save_all_datasets(datasets, output_dir=tmp_path)
    assert len(paths) == 8
    for filename in REQUIRED_CSV_FILES:
        assert (tmp_path / filename).exists()


def test_workbook_builds_with_full_pipeline(tmp_path: Path):
    datasets = generate_all_datasets(seed=42, row_count=100, validate=True)
    context = {**datasets, "inventory": inventory_for_workbook(datasets["inventory"])}
    output = tmp_path / "test.xlsx"
    build_workbook(context, output_path=output)
    assert output.exists()


def test_generate_all_data_includes_workbook_inventory():
    data = generate_all_data()
    from src.services.workbook_inventory import COLUMN_ORDER

    assert list(data["inventory"].columns) == COLUMN_ORDER
