"""
Generate fictional mobile provisioning records.

Produces device issuance and recovery checklist data for interview demos.
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
    "employee_name",
    "department",
    "device_type",
    "asset_tag",
    "imei",
    "sim_number",
    "phone_number",
    "carrier",
    "mdm_enrolled",
    "security_configured",
    "required_apps_installed",
    "user_agreement_signed",
    "date_issued",
    "return_date",
    "status",
]

DEPARTMENTS = [
    "Store Operations",
    "Warehouse",
    "IT",
    "Field Support",
    "Finance",
    "HR",
    "Procurement",
    "Customer Service",
]

CARRIERS = ["Verizon", "AT&T", "T-Mobile"]

DEVICE_TYPES = ["iPhone 15", "iPhone 14", "Samsung Galaxy S24", "Samsung Galaxy A54"]

MOBILE_STATUSES = [
    "Ready",
    "Assigned",
    "Pending Setup",
    "Missing Agreement",
    "Returned",
    "Disabled",
]

# Curated provisioning scenarios
MOBILE_SCENARIOS: list[dict] = [
    {
        "label": "pending_setup",
        "status": "Pending Setup",
        "mdm_enrolled": "No",
        "security_configured": "No",
        "required_apps_installed": "No",
        "user_agreement_signed": "No",
        "return_date": None,
    },
    {
        "label": "assigned",
        "status": "Assigned",
        "mdm_enrolled": "Yes",
        "security_configured": "Yes",
        "required_apps_installed": "Yes",
        "user_agreement_signed": "Yes",
        "return_date": None,
    },
    {
        "label": "missing_agreement",
        "status": "Missing Agreement",
        "mdm_enrolled": "Yes",
        "security_configured": "Yes",
        "required_apps_installed": "Yes",
        "user_agreement_signed": "No",
        "return_date": None,
    },
    {
        "label": "ready",
        "status": "Ready",
        "mdm_enrolled": "Yes",
        "security_configured": "Yes",
        "required_apps_installed": "Yes",
        "user_agreement_signed": "Yes",
        "return_date": None,
    },
    {
        "label": "returned",
        "status": "Returned",
        "mdm_enrolled": "No",
        "security_configured": "No",
        "required_apps_installed": "No",
        "user_agreement_signed": "Yes",
        "return_date": "auto",
    },
]


def _generate_imei(rng: np.random.Generator) -> str:
    """Generate a 15-digit fictional IMEI."""
    return "".join(str(int(x)) for x in rng.integers(0, 10, size=15))


def _generate_phone(rng: np.random.Generator) -> str:
    """Generate a US phone number string."""
    area = int(rng.integers(200, 999))
    prefix = int(rng.integers(200, 999))
    line = int(rng.integers(1000, 9999))
    return f"({area}) {prefix}-{line}"


def _generate_sim(rng: np.random.Generator) -> str:
    """Generate a fictional SIM ICCID."""
    return "8901" + "".join(str(int(x)) for x in rng.integers(0, 10, size=16))


def _build_record(
    index: int,
    employee_name: str,
    department: str,
    device_type: str,
    status: str,
    mdm_enrolled: str,
    security_configured: str,
    required_apps_installed: str,
    user_agreement_signed: str,
    date_issued: date | None,
    return_date: date | None,
    reference: date,
    rng: np.random.Generator,
) -> dict:
    """Assemble a single mobile provisioning record."""
    if date_issued is None and status in ("Assigned", "Missing Agreement", "Returned"):
        date_issued = reference - timedelta(days=int(rng.integers(30, 540)))
    elif date_issued is None and status == "Ready":
        date_issued = None
    elif date_issued is None:
        date_issued = reference - timedelta(days=int(rng.integers(1, 14)))

    return {
        "employee_name": employee_name,
        "department": department,
        "device_type": device_type,
        "asset_tag": f"MOB-{index:05d}",
        "imei": _generate_imei(rng),
        "sim_number": _generate_sim(rng),
        "phone_number": _generate_phone(rng),
        "carrier": CARRIERS[int(rng.integers(0, len(CARRIERS)))],
        "mdm_enrolled": mdm_enrolled,
        "security_configured": security_configured,
        "required_apps_installed": required_apps_installed,
        "user_agreement_signed": user_agreement_signed,
        "date_issued": date_issued,
        "return_date": return_date,
        "status": status,
    }


def _generate_scenario_record(
    index: int,
    scenario: dict,
    reference: date,
    rng: np.random.Generator,
    faker: Faker,
) -> dict:
    """Build a curated mobile provisioning row."""
    return_date = None
    if scenario.get("return_date") == "auto":
        return_date = reference - timedelta(days=int(rng.integers(5, 60)))

    return _build_record(
        index=index,
        employee_name=faker.name(),
        department=DEPARTMENTS[index % len(DEPARTMENTS)],
        device_type=DEVICE_TYPES[index % len(DEVICE_TYPES)],
        status=scenario["status"],
        mdm_enrolled=scenario["mdm_enrolled"],
        security_configured=scenario["security_configured"],
        required_apps_installed=scenario["required_apps_installed"],
        user_agreement_signed=scenario["user_agreement_signed"],
        date_issued=None,
        return_date=return_date,
        reference=reference,
        rng=rng,
    )


def _generate_random_record(
    index: int,
    reference: date,
    rng: np.random.Generator,
    faker: Faker,
) -> dict:
    """Generate a random mobile provisioning record."""
    status = MOBILE_STATUSES[int(rng.integers(0, len(MOBILE_STATUSES)))]
    yes_no = lambda p: "Yes" if rng.random() < p else "No"  # noqa: E731

    if status == "Pending Setup":
        checks = ("No", "No", "No", "No")
    elif status == "Missing Agreement":
        checks = ("Yes", "Yes", "Yes", "No")
    elif status == "Returned":
        checks = ("No", "No", "No", "Yes")
    elif status == "Disabled":
        checks = ("No", "No", "No", "Yes")
    else:
        checks = (yes_no(0.9), yes_no(0.9), yes_no(0.85), yes_no(0.9))

    return_date = None
    if status == "Returned":
        return_date = reference - timedelta(days=int(rng.integers(1, 90)))

    return _build_record(
        index=index,
        employee_name=faker.name(),
        department=DEPARTMENTS[int(rng.integers(0, len(DEPARTMENTS)))],
        device_type=DEVICE_TYPES[int(rng.integers(0, len(DEVICE_TYPES)))],
        status=status,
        mdm_enrolled=checks[0],
        security_configured=checks[1],
        required_apps_installed=checks[2],
        user_agreement_signed=checks[3],
        date_issued=None,
        return_date=return_date,
        reference=reference,
        rng=rng,
    )


def generate_mobile_data(
    row_count: int | None = None,
    seed: int | None = None,
) -> pd.DataFrame:
    """
    Build a DataFrame of fictional mobile provisioning records.

    Args:
        row_count: Number of rows to generate. Defaults to ROW_COUNTS config.
        seed: Random seed for reproducibility. Defaults to RANDOM_SEED config.

    Returns:
        DataFrame with mobile provisioning columns in sheet order.
    """
    row_count = row_count or ROW_COUNTS["mobile"]["default"]
    seed = seed if seed is not None else RANDOM_SEED
    reference = DEMO_REFERENCE_DATE

    rng = np.random.default_rng(seed + 1)  # offset seed from other generators
    faker = Faker()
    Faker.seed(seed + 1)

    records: list[dict] = []
    for i, scenario in enumerate(MOBILE_SCENARIOS, start=1):
        records.append(_generate_scenario_record(i, scenario, reference, rng, faker))

    for i in range(len(MOBILE_SCENARIOS) + 1, row_count + 1):
        records.append(_generate_random_record(i, reference, rng, faker))

    return pd.DataFrame(records, columns=COLUMN_ORDER)


def save_mobile_data(df: pd.DataFrame, output_dir: Path | None = None) -> Path:
    """Write mobile provisioning data to CSV in data/generated/."""
    output_dir = output_dir or DATA_GENERATED_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / CSV_FILES["mobile"]
    df.to_csv(path, index=False, date_format="%Y-%m-%d")
    return path
