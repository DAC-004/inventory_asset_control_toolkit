"""
Entry point for the Inventory & IT Asset Control Toolkit build process.

Usage (from project root):
    python src/main.py

Generates:
    dist/Inventory_IT_Asset_Control_Toolkit.xlsx
    data/generated/*.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path when running as `python src/main.py`
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.workbook_config import (  # noqa: E402
    DATA_GENERATED_DIR,
    DIST_DIR,
    RANDOM_SEED,
    ROW_COUNTS,
    SHEET_ORDER,
    VERSION,
    WORKBOOK_PATH,
    WORKBOOK_TITLE,
)
from src.data_generation.generate_disposal import generate_disposal_data, save_disposal_data  # noqa: E402
from src.data_generation.generate_inventory import generate_inventory_data, save_inventory_data  # noqa: E402
from src.data_generation.generate_it_assets import generate_it_asset_data, save_it_asset_data  # noqa: E402
from src.data_generation.generate_mobile import generate_mobile_data, save_mobile_data  # noqa: E402
from src.data_generation.generate_software import generate_software_data, save_software_data  # noqa: E402
from src.workbook.builder import build_workbook  # noqa: E402


def _log(message: str) -> None:
    """Print a user-facing progress message."""
    print(message)


def ensure_output_directories() -> None:
    """Create dist/ and data/generated/ if they do not exist."""
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    DATA_GENERATED_DIR.mkdir(parents=True, exist_ok=True)


def generate_all_data() -> dict:
    """
    Run all data generators and persist CSVs to data/generated/.

    Returns:
        Dict of DataFrames keyed by domain name.
    """
    _log("  Generating inventory records...")
    inventory_df = generate_inventory_data(
        row_count=ROW_COUNTS["inventory"]["default"],
        seed=RANDOM_SEED,
    )
    _log("  Generating IT asset records...")
    it_assets_df = generate_it_asset_data(
        row_count=ROW_COUNTS["it_assets"]["default"],
        seed=RANDOM_SEED,
    )
    _log("  Generating software license records...")
    software_df = generate_software_data(
        row_count=ROW_COUNTS["software"]["default"],
        seed=RANDOM_SEED,
    )
    _log("  Generating mobile provisioning records...")
    mobile_df = generate_mobile_data(
        row_count=ROW_COUNTS["mobile"]["default"],
        seed=RANDOM_SEED,
    )
    _log("  Generating disposal log records...")
    disposal_df = generate_disposal_data(
        row_count=ROW_COUNTS["disposal"]["default"],
        seed=RANDOM_SEED,
    )

    datasets = {
        "inventory": inventory_df,
        "it_assets": it_assets_df,
        "software": software_df,
        "mobile": mobile_df,
        "disposal": disposal_df,
    }

    _log(f"  Saving CSV files to {DATA_GENERATED_DIR}/")
    save_paths = {
        "inventory": save_inventory_data(inventory_df),
        "it_assets": save_it_asset_data(it_assets_df),
        "software": save_software_data(software_df),
        "mobile": save_mobile_data(mobile_df),
        "disposal": save_disposal_data(disposal_df),
    }

    for key, path in save_paths.items():
        row_count = len(datasets[key])
        _log(f"    {path.name} ({row_count:,} rows)")

    return datasets


def main() -> int:
    """Generate sample data and build the Excel workbook."""
    step = "startup"
    try:
        _log(f"{WORKBOOK_TITLE} {VERSION}")
        _log("=" * 60)

        step = "creating output folders"
        _log("Step 1/4: Creating required folders...")
        ensure_output_directories()
        _log(f"  dist/          -> {DIST_DIR}")
        _log(f"  data/generated -> {DATA_GENERATED_DIR}")

        step = "generating sample data"
        _log("Step 2/4: Generating fictional sample data...")
        data = generate_all_data()

        step = "building workbook"
        _log("Step 3/4: Building Excel workbook...")
        output_path = build_workbook(data, output_path=WORKBOOK_PATH)
        _log("  Sheets: {0} tabs in required order".format(len(SHEET_ORDER)))

        step = "finishing"
        _log("Step 4/4: Verifying output...")
        if not output_path.exists():
            raise FileNotFoundError(f"Expected workbook was not created: {output_path}")

        _log("=" * 60)
        _log("Build completed successfully.")
        _log(f"Workbook: {output_path.resolve()}")
        _log(f"CSV data: {DATA_GENERATED_DIR.resolve()}/")
        return 0

    except KeyboardInterrupt:
        print("\nBuild cancelled by user.", file=sys.stderr)
        return 130

    except Exception as exc:
        print(f"\nBuild failed during: {step}", file=sys.stderr)
        print(f"  {type(exc).__name__}: {exc}", file=sys.stderr)
        print(
            "  Check that dependencies are installed: pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
