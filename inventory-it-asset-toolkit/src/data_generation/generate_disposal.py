"""
Generate fictional asset disposal records.

Produces lifecycle retirement and data-destruction scenarios for interview demos.
Output is deterministic when the same seed is used.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

from config.workbook_config import (
    CSV_FILES,
    DATA_GENERATED_DIR,
    DEMO_REFERENCE_DATE,
    RANDOM_SEED,
    ROW_COUNTS,
)

COLUMN_ORDER = [
    "asset_tag",
    "serial_number",
    "device_type",
    "assigned_user",
    "return_date",
    "condition",
    "data_wipe_required",
    "data_wipe_completed",
    "wipe_method",
    "disposal_vendor",
    "certificate_received",
    "disposal_date",
    "approved_by",
    "disposal_status",
]

DEVICE_TYPES = [
    "Laptop",
    "Desktop",
    "Mobile Phone",
    "Printer",
    "Monitor",
    "Scanner",
]

CONDITIONS = ["Good", "Fair", "Poor", "Damaged", "Non-Functional"]

WIPE_METHODS = ["NIST 800-88 Clear", "DOD 5220.22-M", "Physical Destruction", ""]

DISPOSAL_VENDORS = [
    "EcoCycle IT Disposal",
    "SecureShred Electronics",
    "Metro E-Waste Partners",
    "",
]

APPROVERS = [
    "Daniel A. Cruz",
    "Patricia Nguyen",
    "Robert Kim",
    "Sandra Lopez",
]

# Curated disposal scenarios
DISPOSAL_SCENARIOS: list[dict] = [
    {
        "label": "pending_wipe",
        "data_wipe_required": "Yes",
        "data_wipe_completed": "No",
        "certificate_received": "No",
        "wipe_method": "",
        "disposal_vendor": "",
        "disposal_date": None,
    },
    {
        "label": "certificate_missing",
        "data_wipe_required": "Yes",
        "data_wipe_completed": "Yes",
        "certificate_received": "No",
        "wipe_method": "NIST 800-88 Clear",
        "disposal_vendor": "EcoCycle IT Disposal",
        "disposal_date": None,
    },
    {
        "label": "disposed",
        "data_wipe_required": "Yes",
        "data_wipe_completed": "Yes",
        "certificate_received": "Yes",
        "wipe_method": "NIST 800-88 Clear",
        "disposal_vendor": "SecureShred Electronics",
        "disposal_date": "auto",
    },
    {
        "label": "hold_for_review",
        "data_wipe_required": "No",
        "data_wipe_completed": "No",
        "certificate_received": "No",
        "wipe_method": "",
        "disposal_vendor": "",
        "disposal_date": None,
    },
    {
        "label": "wiped_pending_vendor",
        "data_wipe_required": "Yes",
        "data_wipe_completed": "Yes",
        "certificate_received": "No",
        "wipe_method": "DOD 5220.22-M",
        "disposal_vendor": "Metro E-Waste Partners",
        "disposal_date": None,
    },
]


def assign_disposal_status(
    data_wipe_required: str,
    data_wipe_completed: str,
    certificate_received: str,
) -> str:
    """Apply disposal status rules in priority order (specs §7.5)."""
    if data_wipe_required == "Yes" and data_wipe_completed == "No":
        return "Pending Wipe"
    if data_wipe_completed == "Yes" and certificate_received == "No":
        return "Certificate Missing"
    if data_wipe_completed == "Yes" and certificate_received == "Yes":
        return "Disposed"
    return "Hold for Review"


def _build_record(
    index: int,
    device_type: str,
    assigned_user: str,
    return_date: date,
    condition: str,
    data_wipe_required: str,
    data_wipe_completed: str,
    wipe_method: str,
    disposal_vendor: str,
    certificate_received: str,
    disposal_date: date | None,
    approved_by: str,
    reference: date,
    rng: np.random.Generator,
) -> dict:
    """Assemble a single disposal log record."""
    serial_suffix = "".join(str(int(x)) for x in rng.integers(0, 10, size=8))
    disposal_status = assign_disposal_status(
        data_wipe_required, data_wipe_completed, certificate_received
    )

    return {
        "asset_tag": f"DSP-{index:05d}",
        "serial_number": f"SN{serial_suffix}",
        "device_type": device_type,
        "assigned_user": assigned_user,
        "return_date": return_date,
        "condition": condition,
        "data_wipe_required": data_wipe_required,
        "data_wipe_completed": data_wipe_completed,
        "wipe_method": wipe_method,
        "disposal_vendor": disposal_vendor,
        "certificate_received": certificate_received,
        "disposal_date": disposal_date,
        "approved_by": approved_by,
        "disposal_status": disposal_status,
    }


def _generate_scenario_record(
    index: int,
    scenario: dict,
    reference: date,
    rng: np.random.Generator,
    faker: Faker,
) -> dict:
    """Build a curated disposal log row."""
    return_date = reference - timedelta(days=int(rng.integers(10, 120)))
    disposal_date = None
    if scenario.get("disposal_date") == "auto":
        disposal_date = reference - timedelta(days=int(rng.integers(1, 30)))

    # Force pending vendor pickup label for scenario 5
    disposal_status_override = None
    if scenario["label"] == "wiped_pending_vendor":
        disposal_status_override = "Pending Vendor Pickup"

    record = _build_record(
        index=index,
        device_type=DEVICE_TYPES[index % len(DEVICE_TYPES)],
        assigned_user=faker.name(),
        return_date=return_date,
        condition=CONDITIONS[index % len(CONDITIONS)],
        data_wipe_required=scenario["data_wipe_required"],
        data_wipe_completed=scenario["data_wipe_completed"],
        wipe_method=scenario["wipe_method"],
        disposal_vendor=scenario["disposal_vendor"],
        certificate_received=scenario["certificate_received"],
        disposal_date=disposal_date,
        approved_by=APPROVERS[index % len(APPROVERS)],
        reference=reference,
        rng=rng,
    )

    if disposal_status_override:
        record["disposal_status"] = disposal_status_override

    return record


def _generate_random_record(
    index: int,
    reference: date,
    rng: np.random.Generator,
    faker: Faker,
) -> dict:
    """Generate a random disposal log record."""
    data_wipe_required = "Yes" if rng.random() < 0.85 else "No"
    data_wipe_completed = "Yes" if data_wipe_required == "Yes" and rng.random() < 0.6 else "No"
    certificate_received = (
        "Yes" if data_wipe_completed == "Yes" and rng.random() < 0.5 else "No"
    )
    wipe_method = WIPE_METHODS[int(rng.integers(0, len(WIPE_METHODS)))] if data_wipe_completed == "Yes" else ""
    disposal_vendor = DISPOSAL_VENDORS[int(rng.integers(0, len(DISPOSAL_VENDORS)))]
    disposal_date = None
    if certificate_received == "Yes":
        disposal_date = reference - timedelta(days=int(rng.integers(1, 60)))

    return _build_record(
        index=index,
        device_type=DEVICE_TYPES[int(rng.integers(0, len(DEVICE_TYPES)))],
        assigned_user=faker.name(),
        return_date=reference - timedelta(days=int(rng.integers(5, 180))),
        condition=CONDITIONS[int(rng.integers(0, len(CONDITIONS)))],
        data_wipe_required=data_wipe_required,
        data_wipe_completed=data_wipe_completed,
        wipe_method=wipe_method,
        disposal_vendor=disposal_vendor,
        certificate_received=certificate_received,
        disposal_date=disposal_date,
        approved_by=APPROVERS[int(rng.integers(0, len(APPROVERS)))],
        reference=reference,
        rng=rng,
    )


def generate_disposal_data(
    row_count: int | None = None,
    seed: int | None = None,
) -> pd.DataFrame:
    """
    Build a DataFrame of fictional disposal log records.

    Args:
        row_count: Number of rows to generate. Defaults to ROW_COUNTS config.
        seed: Random seed for reproducibility. Defaults to RANDOM_SEED config.

    Returns:
        DataFrame with disposal log columns in sheet order.
    """
    row_count = row_count or ROW_COUNTS["disposal"]["default"]
    seed = seed if seed is not None else RANDOM_SEED
    reference = DEMO_REFERENCE_DATE

    rng = np.random.default_rng(seed + 2)
    faker = Faker()
    Faker.seed(seed + 2)

    records: list[dict] = []
    for i, scenario in enumerate(DISPOSAL_SCENARIOS, start=1):
        records.append(_generate_scenario_record(i, scenario, reference, rng, faker))

    for i in range(len(DISPOSAL_SCENARIOS) + 1, row_count + 1):
        records.append(_generate_random_record(i, reference, rng, faker))

    df = pd.DataFrame(records, columns=COLUMN_ORDER)

    for idx in df.index:
        row = df.loc[idx]
        if row["disposal_status"] not in ("Pending Vendor Pickup",):
            df.at[idx, "disposal_status"] = assign_disposal_status(
                str(row["data_wipe_required"]),
                str(row["data_wipe_completed"]),
                str(row["certificate_received"]),
            )

    return df


def save_disposal_data(df: pd.DataFrame, output_dir: Path | None = None) -> Path:
    """Write disposal data to CSV in data/generated/."""
    output_dir = output_dir or DATA_GENERATED_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / CSV_FILES["disposal"]
    df.to_csv(path, index=False, date_format="%Y-%m-%d")
    return path
