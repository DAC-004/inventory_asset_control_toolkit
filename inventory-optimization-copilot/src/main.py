"""
Entry point for the Inventory Optimization Copilot build process.

Usage (from project root):
    python src/main.py

Generates:
    dist/Inventory_Optimization_Copilot.xlsx
    data/generated/*.csv (8 inventory planning datasets)
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.workbook_config import (  # noqa: E402
    CSV_FILES,
    DATA_GENERATED_DIR,
    DIST_DIR,
    RANDOM_SEED,
    ROW_COUNTS,
    SHEET_ORDER,
    VERSION,
    WORKBOOK_PATH,
    WORKBOOK_TITLE,
)
from src.data_generation.pipeline import (  # noqa: E402
    generate_all_datasets,
    save_all_datasets,
)
from src.services.workbook_inventory import inventory_for_workbook  # noqa: E402
from src.workbook.builder import build_workbook  # noqa: E402


def _log(message: str) -> None:
    print(message)


def ensure_output_directories() -> None:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    DATA_GENERATED_DIR.mkdir(parents=True, exist_ok=True)


def generate_all_data() -> dict:
    """
    Run full data pipeline, validate, persist CSVs, return workbook context.

    Returns:
        Dict with full datasets plus workbook-projected inventory.
    """
    datasets = generate_all_datasets(
        seed=RANDOM_SEED,
        row_count=ROW_COUNTS["inventory"]["default"],
        validate=True,
    )
    paths = save_all_datasets(datasets)
    _log(f"  Saving CSV files to {DATA_GENERATED_DIR}/")
    for key, path in paths.items():
        _log(f"    {path.name} ({len(datasets[key]):,} rows)")

    return {
        **datasets,
        "inventory_full": datasets["inventory"],
        "inventory": inventory_for_workbook(datasets["inventory"]),
    }


def main() -> int:
    step = "startup"
    try:
        _log(f"{WORKBOOK_TITLE} {VERSION}")
        _log("=" * 60)

        step = "creating output folders"
        _log("Step 1/4: Creating required folders...")
        ensure_output_directories()

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
        _log(f"CSV data: {DATA_GENERATED_DIR.resolve()}/ ({len(CSV_FILES)} files)")
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
