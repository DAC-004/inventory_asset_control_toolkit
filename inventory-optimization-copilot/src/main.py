"""
Entry point for the Inventory Optimization Copilot build process.

Usage (from project root):
    python src/main.py

Generates:
    dist/Inventory_Optimization_Copilot.xlsx
    data/generated/inventory_data.csv
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
from src.data_generation.generate_inventory import (  # noqa: E402
    generate_inventory_data,
    save_inventory_data,
)
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
    Run inventory data generation and persist CSV to data/generated/.

    Returns:
        Dict of DataFrames keyed by domain name.
    """
    _log("  Generating inventory records...")
    inventory_df = generate_inventory_data(
        row_count=ROW_COUNTS["inventory"]["default"],
        seed=RANDOM_SEED,
    )

    datasets = {"inventory": inventory_df}

    _log(f"  Saving CSV files to {DATA_GENERATED_DIR}/")
    path = save_inventory_data(inventory_df)
    _log(f"    {path.name} ({len(inventory_df):,} rows)")

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
