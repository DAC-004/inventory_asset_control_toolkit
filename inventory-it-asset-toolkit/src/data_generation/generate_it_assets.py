"""
Generate fictional IT asset records for the IT Asset Register and audit sheets.

Produces realistic NYC metro fleet data for interview demos.
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
    "make",
    "model",
    "assigned_user",
    "department",
    "location",
    "borough",
    "purchase_date",
    "warranty_expiration",
    "status",
    "condition",
    "last_audit_date",
    "lifecycle_stage",
    "notes",
]

DEVICE_CATALOG: list[tuple[str, str, str]] = [
    ("Laptop", "Dell", "Latitude 5540"),
    ("Laptop", "Lenovo", "ThinkPad T14"),
    ("Laptop", "HP", "EliteBook 840 G10"),
    ("Desktop", "Dell", "OptiPlex 7010"),
    ("Desktop", "HP", "ProDesk 400 G9"),
    ("Printer", "HP", "LaserJet Pro M404dn"),
    ("Printer", "Canon", "imageCLASS MF455dw"),
    ("Scanner", "Fujitsu", "fi-7160"),
    ("Mobile Phone", "Apple", "iPhone 15"),
    ("Mobile Phone", "Samsung", "Galaxy S24"),
    ("Monitor", "Dell", "UltraSharp U2723QE"),
    ("Monitor", "LG", "27BN85U-N"),
    ("Network Device", "Cisco", "Meraki MR46"),
    ("Network Device", "Ubiquiti", "UniFi AP U6 Pro"),
]

LOCATIONS: list[tuple[str, str]] = [
    ("DC-NY", "Queens"),
    ("DC-NJ", "Newark"),
    ("DC-PA", "Allentown"),
    ("Store-Bronx", "Bronx"),
    ("Store-Queens", "Queens"),
    ("Store-Brooklyn", "Brooklyn"),
    ("Store-Manhattan", "Manhattan"),
    ("Store-WhitePlains", "Westchester"),
    ("Store-Yonkers", "Westchester"),
    ("Store-Newark", "Newark"),
    ("Store-Stamford", "Stamford"),
    ("HQ-Queens", "Queens"),
]

DEPARTMENTS = [
    "IT",
    "Store Operations",
    "Warehouse",
    "Finance",
    "HR",
    "Procurement",
    "Customer Service",
    "Field Support",
]

CONDITIONS = ["Excellent", "Good", "Fair", "Poor", "Damaged"]

# Curated rows covering required interview scenarios
STATUS_SCENARIOS: list[dict] = [
    {
        "label": "assigned",
        "status": "Assigned",
        "lifecycle_stage": "Assigned",
        "assigned_user": "Maria Gonzalez",
        "condition": "Good",
        "notes": "Primary workstation — annual audit current.",
    },
    {
        "label": "in_stock",
        "status": "In Stock",
        "lifecycle_stage": "In Stock",
        "assigned_user": "",
        "condition": "Excellent",
        "notes": "Spare pool device — ready for deployment.",
    },
    {
        "label": "missing",
        "status": "Missing",
        "lifecycle_stage": "Assigned",
        "assigned_user": "James Rivera",
        "condition": "Unknown",
        "notes": "Not located during Q2 physical audit — follow-up open.",
    },
    {
        "label": "retired",
        "status": "Retired",
        "lifecycle_stage": "Retired",
        "assigned_user": "",
        "condition": "Fair",
        "notes": "End of life — removed from active inventory.",
    },
    {
        "label": "pending_disposal",
        "status": "Returned",
        "lifecycle_stage": "Retired",
        "assigned_user": "Former Employee",
        "condition": "Poor",
        "notes": "Pending disposal — awaiting data wipe and vendor pickup.",
    },
    {
        "label": "in_repair",
        "status": "In Repair",
        "lifecycle_stage": "In Repair",
        "assigned_user": "Carlos Mendez",
        "condition": "Damaged",
        "notes": "Keyboard replacement — vendor RMA in progress.",
    },
    {
        "label": "disposed",
        "status": "Disposed",
        "lifecycle_stage": "Disposed",
        "assigned_user": "",
        "condition": "Poor",
        "notes": "Disposed per certificate IT-DSP-2025-0142.",
    },
]


def _device_tag_prefix(device_type: str) -> str:
    """Map device type to asset tag prefix."""
    prefixes = {
        "Laptop": "LAP",
        "Desktop": "DSK",
        "Printer": "PRT",
        "Scanner": "SCN",
        "Mobile Phone": "MOB",
        "Monitor": "MON",
        "Network Device": "NET",
    }
    return prefixes.get(device_type, "AST")


def _build_record(
    index: int,
    device: tuple[str, str, str],
    location: tuple[str, str],
    status: str,
    lifecycle_stage: str,
    assigned_user: str,
    department: str,
    condition: str,
    notes: str,
    purchase_date: date,
    reference: date,
    rng: np.random.Generator,
) -> dict:
    """Assemble a single IT asset record."""
    device_type, make, model = device
    location_name, borough = location
    prefix = _device_tag_prefix(device_type)

    warranty_years = 3 if device_type in ("Laptop", "Desktop", "Mobile Phone") else 1
    warranty_expiration = purchase_date + timedelta(days=365 * warranty_years)
    audit_days_ago = int(rng.integers(5, 120))
    last_audit_date = reference - timedelta(days=audit_days_ago)

    serial_suffix = "".join(str(int(x)) for x in rng.integers(0, 10, size=8))
    serial_number = f"{make[:3].upper()}{serial_suffix}"

    return {
        "asset_tag": f"{prefix}-{index:05d}",
        "serial_number": serial_number,
        "device_type": device_type,
        "make": make,
        "model": model,
        "assigned_user": assigned_user,
        "department": department,
        "location": location_name,
        "borough": borough,
        "purchase_date": purchase_date,
        "warranty_expiration": warranty_expiration,
        "status": status,
        "condition": condition,
        "last_audit_date": last_audit_date,
        "lifecycle_stage": lifecycle_stage,
        "notes": notes,
    }


def _generate_scenario_record(
    index: int,
    scenario: dict,
    reference: date,
    rng: np.random.Generator,
) -> dict:
    """Build a curated IT asset row for a required scenario."""
    device = DEVICE_CATALOG[index % len(DEVICE_CATALOG)]
    location = LOCATIONS[index % len(LOCATIONS)]
    purchase_date = reference - timedelta(days=int(rng.integers(180, 1400)))
    department = DEPARTMENTS[index % len(DEPARTMENTS)]

    return _build_record(
        index=index,
        device=device,
        location=location,
        status=scenario["status"],
        lifecycle_stage=scenario["lifecycle_stage"],
        assigned_user=scenario["assigned_user"],
        department=department,
        condition=scenario["condition"],
        notes=scenario["notes"],
        purchase_date=purchase_date,
        reference=reference,
        rng=rng,
    )


def _generate_random_record(
    index: int,
    reference: date,
    rng: np.random.Generator,
    faker: Faker,
) -> dict:
    """Generate a random IT asset with weighted status distribution."""
    device = DEVICE_CATALOG[int(rng.integers(0, len(DEVICE_CATALOG)))]
    location = LOCATIONS[int(rng.integers(0, len(LOCATIONS)))]
    department = DEPARTMENTS[int(rng.integers(0, len(DEPARTMENTS)))]
    purchase_date = reference - timedelta(days=int(rng.integers(90, 1825)))

    status_weights = [
        ("Assigned", 45),
        ("In Stock", 20),
        ("In Repair", 8),
        ("Returned", 5),
        ("Retired", 5),
        ("Missing", 3),
        ("Disposed", 4),
    ]
    statuses, weights = zip(*status_weights)
    status = statuses[int(rng.choice(len(statuses), p=np.array(weights) / sum(weights)))]

    lifecycle_map = {
        "Assigned": "Assigned",
        "In Stock": "In Stock",
        "In Repair": "In Repair",
        "Returned": "Returned",
        "Retired": "Retired",
        "Missing": "Assigned",
        "Disposed": "Disposed",
    }
    lifecycle_stage = lifecycle_map[status]
    assigned_user = faker.name() if status in ("Assigned", "In Repair", "Missing") else ""
    condition = CONDITIONS[int(rng.integers(0, len(CONDITIONS)))]
    notes = "" if status == "Assigned" else f"Auto-generated record — status {status}."

    return _build_record(
        index=index,
        device=device,
        location=location,
        status=status,
        lifecycle_stage=lifecycle_stage,
        assigned_user=assigned_user,
        department=department,
        condition=condition,
        notes=notes,
        purchase_date=purchase_date,
        reference=reference,
        rng=rng,
    )


def generate_it_asset_data(
    row_count: int | None = None,
    seed: int | None = None,
) -> pd.DataFrame:
    """
    Build a DataFrame of fictional IT asset records.

    Args:
        row_count: Number of rows to generate. Defaults to ROW_COUNTS config.
        seed: Random seed for reproducibility. Defaults to RANDOM_SEED config.

    Returns:
        DataFrame with IT asset columns in sheet order.
    """
    row_count = row_count or ROW_COUNTS["it_assets"]["default"]
    seed = seed if seed is not None else RANDOM_SEED
    reference = DEMO_REFERENCE_DATE

    rng = np.random.default_rng(seed)
    faker = Faker()
    Faker.seed(seed)

    records: list[dict] = []
    for i, scenario in enumerate(STATUS_SCENARIOS, start=1):
        records.append(_generate_scenario_record(i, scenario, reference, rng))

    for i in range(len(STATUS_SCENARIOS) + 1, row_count + 1):
        records.append(_generate_random_record(i, reference, rng, faker))

    return pd.DataFrame(records, columns=COLUMN_ORDER)


def save_it_asset_data(df: pd.DataFrame, output_dir: Path | None = None) -> Path:
    """Write IT asset data to CSV in data/generated/."""
    output_dir = output_dir or DATA_GENERATED_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / CSV_FILES["it_assets"]
    df.to_csv(path, index=False, date_format="%Y-%m-%d")
    return path
