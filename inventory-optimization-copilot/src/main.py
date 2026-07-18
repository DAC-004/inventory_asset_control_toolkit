"""
Entry point for the Inventory Optimization Copilot build process.

Usage (from project root):
    python src/main.py

Generates:
    dist/Inventory_Optimization_Copilot.xlsx
    data/generated/*.csv (8 inventory planning datasets)
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.workbook_config import (  # noqa: E402
    AS_OF_DATE,
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
from src.exceptions import BuildProcessError  # noqa: E402
from src.services.workbook_inventory import inventory_for_workbook  # noqa: E402
from src.workbook.builder import build_workbook  # noqa: E402
from src.workbook.validator import validate_workbook_file  # noqa: E402

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure structured console logging for the build pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | %(message)s",
    )


def ensure_output_directories() -> None:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    DATA_GENERATED_DIR.mkdir(parents=True, exist_ok=True)


def generate_all_data() -> dict:
    """
    Run full data pipeline, validate, persist CSVs, return workbook context.

    Returns:
        Dict with full datasets plus workbook-projected inventory.
    """
    row_count = ROW_COUNTS["inventory"]["default"]
    logger.info(
        "Generating datasets | seed=%s as_of=%s rows=%s",
        RANDOM_SEED,
        AS_OF_DATE.isoformat(),
        row_count,
    )

    datasets = generate_all_datasets(
        seed=RANDOM_SEED,
        row_count=row_count,
        validate=True,
    )
    logger.info("Dataset validation passed")

    paths = save_all_datasets(datasets)
    logger.info("Saving CSV files to %s/", DATA_GENERATED_DIR.name)
    for key, path in paths.items():
        logger.info("  %s: %s rows", path.name, f"{len(datasets[key]):,}")

    return {
        **datasets,
        "inventory_full": datasets["inventory"],
        "inventory": inventory_for_workbook(datasets["inventory"]),
    }


def main() -> int:
    configure_logging()
    started = time.perf_counter()
    step = "startup"

    try:
        logger.info("Build started | %s %s", WORKBOOK_TITLE, VERSION)
        logger.info(
            "Configuration | seed=%s as_of=%s sheets=%s",
            RANDOM_SEED,
            AS_OF_DATE.isoformat(),
            len(SHEET_ORDER),
        )

        step = "creating output folders"
        logger.info("Step 1/4: Creating required folders...")
        ensure_output_directories()

        step = "generating sample data"
        logger.info("Step 2/4: Generating fictional sample data...")
        data = generate_all_data()

        step = "building workbook"
        logger.info("Step 3/4: Building Excel workbook...")
        output_path = build_workbook(data, output_path=WORKBOOK_PATH)
        logger.info("Sheets created: %s tabs in required order", len(SHEET_ORDER))

        step = "verifying output"
        logger.info("Step 4/4: Verifying output...")
        validate_workbook_file(output_path)

        elapsed = time.perf_counter() - started
        size_kb = output_path.stat().st_size / 1024
        logger.info("Build completed successfully in %.1fs", elapsed)
        logger.info("Workbook: %s (%.1f KB)", output_path.name, size_kb)
        logger.info("CSV data: %s/ (%s files)", DATA_GENERATED_DIR.name, len(CSV_FILES))
        return 0

    except KeyboardInterrupt:
        logger.error("Build cancelled by user")
        return 130

    except BuildProcessError as exc:
        elapsed = time.perf_counter() - started
        logger.error("Build failed during %s after %.1fs: %s", step, elapsed, exc)
        return 1

    except Exception as exc:
        elapsed = time.perf_counter() - started
        logger.error(
            "Build failed during %s after %.1fs: %s: %s",
            step,
            elapsed,
            type(exc).__name__,
            exc,
        )
        logger.error("Install dependencies with: pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
