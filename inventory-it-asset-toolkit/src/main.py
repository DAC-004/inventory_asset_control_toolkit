"""
Entry point for the Inventory & IT Asset Control Toolkit build process.

Usage (from project root):
    python src/main.py

Generates:
    dist/Inventory_IT_Asset_Control_Toolkit.xlsx
    data/generated/*.csv
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path when running as `python src/main.py`
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.workbook_config import (
    DATA_GENERATED_DIR,
    DIST_DIR,
    RANDOM_SEED,
    ROW_COUNTS,
    WORKBOOK_PATH,
)
from src.data_generation.generate_disposal import generate_disposal_data, save_disposal_data
from src.data_generation.generate_inventory import generate_inventory_data, save_inventory_data
from src.data_generation.generate_it_assets import generate_it_asset_data, save_it_asset_data
from src.data_generation.generate_mobile import generate_mobile_data, save_mobile_data
from src.data_generation.generate_software import generate_software_data, save_software_data
from src.workbook.builder import build_workbook


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
    inventory_df = generate_inventory_data(
        row_count=ROW_COUNTS["inventory"]["default"],
        seed=RANDOM_SEED,
    )
    it_assets_df = generate_it_asset_data(
        row_count=ROW_COUNTS["it_assets"]["default"],
        seed=RANDOM_SEED,
    )
    software_df = generate_software_data(
        row_count=ROW_COUNTS["software"]["default"],
        seed=RANDOM_SEED,
    )
    mobile_df = generate_mobile_data(
        row_count=ROW_COUNTS["mobile"]["default"],
        seed=RANDOM_SEED,
    )
    disposal_df = generate_disposal_data(
        row_count=ROW_COUNTS["disposal"]["default"],
        seed=RANDOM_SEED,
    )

    save_inventory_data(inventory_df)
    save_it_asset_data(it_assets_df)
    save_software_data(software_df)
    save_mobile_data(mobile_df)
    save_disposal_data(disposal_df)

    return {
        "inventory": inventory_df,
        "it_assets": it_assets_df,
        "software": software_df,
        "mobile": mobile_df,
        "disposal": disposal_df,
    }


def main() -> int:
    """Generate sample data and build the Excel workbook."""
    try:
        ensure_output_directories()
        data = generate_all_data()
        output_path = build_workbook(data)
        print(f"Workbook created successfully: {output_path}")
        return 0
    except Exception as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
