"""Inventory data loading from Excel and CSV sources."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config.constants import APP_ROOT, EXCEL_SHEET_CANDIDATES
from src.utils.exceptions import DataLoadError
from src.utils.logging import get_logger

logger = get_logger(__name__)


def load_inventory_data(source_path: Path | str | None = None) -> pd.DataFrame:
    """Load raw inventory data from Excel workbook or CSV file."""
    if source_path is None:
        source_path = APP_ROOT / "data" / "sample" / "sample_inventory.csv"
    path = Path(source_path)

    if not path.exists():
        raise DataLoadError(f"Data source not found: {path}")

    logger.info("Loading inventory data from %s", path)

    if path.suffix.lower() in {".xlsx", ".xlsm", ".xls"}:
        return _load_excel(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    raise DataLoadError(f"Unsupported file format: {path.suffix}")


def _load_excel(path: Path) -> pd.DataFrame:
    xl = pd.ExcelFile(path)
    sheet_name = _select_inventory_sheet(xl.sheet_names)
    preview = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=6)
    header_row = _detect_header_row(preview)
    return pd.read_excel(path, sheet_name=sheet_name, header=header_row)


def _select_inventory_sheet(sheet_names: list[str]) -> str:
    for sheet in EXCEL_SHEET_CANDIDATES:
        if sheet in sheet_names:
            return sheet
    for sheet in sheet_names:
        if "inventory" in sheet.lower() and "dashboard" not in sheet.lower():
            return sheet
    return sheet_names[0]


def _detect_header_row(preview: pd.DataFrame) -> int:
    """Find the row containing SKU column headers in formatted workbook exports."""
    header_markers = {"sku", "item id", "product name", "quantity on hand"}
    for idx, row in preview.iterrows():
        values = {str(v).strip().lower() for v in row.tolist() if pd.notna(v)}
        if values & header_markers:
            return int(idx)
    return 0
