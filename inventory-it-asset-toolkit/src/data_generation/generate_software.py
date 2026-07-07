"""
Generate fictional software license records.

Produces compliance and renewal scenarios for interview demos.
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
    SOFTWARE_RENEWAL_THRESHOLDS,
)

COLUMN_ORDER = [
    "software_name",
    "vendor",
    "license_type",
    "purchased_licenses",
    "assigned_licenses",
    "available_licenses",
    "renewal_date",
    "days_until_renewal",
    "department",
    "owner",
    "annual_cost",
    "compliance_status",
]

SOFTWARE_CATALOG: list[tuple[str, str, str, float]] = [
    ("Microsoft 365 E3", "Microsoft", "Subscription", 45000.00),
    ("Adobe Creative Cloud", "Adobe", "Subscription", 12800.00),
    ("Zoom Business", "Zoom", "Subscription", 6200.00),
    ("Slack Enterprise Grid", "Salesforce", "Subscription", 18500.00),
    ("ServiceNow ITSM", "ServiceNow", "Subscription", 92000.00),
    ("CrowdStrike Falcon", "CrowdStrike", "Subscription", 34000.00),
    ("Okta SSO", "Okta", "Subscription", 15600.00),
    ("AutoCAD LT", "Autodesk", "Perpetual + Maintenance", 8900.00),
    ("Tableau Creator", "Salesforce", "Subscription", 11200.00),
    ("DocuSign Business Pro", "DocuSign", "Subscription", 4800.00),
    ("Jira Software", "Atlassian", "Subscription", 7600.00),
    ("Confluence", "Atlassian", "Subscription", 5400.00),
    ("VMware vSphere", "Broadcom", "Subscription", 42000.00),
    ("Backup Exec", "Veritas", "Subscription", 9800.00),
    ("SQL Server Standard", "Microsoft", "Perpetual", 22000.00),
]

DEPARTMENTS = ["IT", "Finance", "HR", "Store Operations", "Warehouse", "Procurement"]

# Curated compliance / renewal scenarios
COMPLIANCE_SCENARIOS: list[dict] = [
    {
        "label": "over_assigned",
        "purchased": 50,
        "assigned": 58,
        "days_until_renewal": 120,
    },
    {
        "label": "renewal_30_days",
        "purchased": 200,
        "assigned": 185,
        "days_until_renewal": 22,
    },
    {
        "label": "renewal_60_days",
        "purchased": 75,
        "assigned": 70,
        "days_until_renewal": 60,
    },
    {
        "label": "renewal_90_days",
        "purchased": 120,
        "assigned": 115,
        "days_until_renewal": 90,
    },
    {
        "label": "compliant",
        "purchased": 300,
        "assigned": 245,
        "days_until_renewal": 200,
    },
]


def assign_compliance_status(
    purchased_licenses: int,
    assigned_licenses: int,
    days_until_renewal: int,
) -> str:
    """Apply software compliance rules in priority order (specs §7.4)."""
    thresholds = SOFTWARE_RENEWAL_THRESHOLDS

    if assigned_licenses > purchased_licenses:
        return "Over-Assigned"
    if days_until_renewal <= thresholds["renewal_due_soon_days"]:
        return "Renewal Due Soon"
    if days_until_renewal <= thresholds["renewal_watch_days"]:
        return "Renewal Watch"
    return "Compliant"


def _build_record(
    index: int,
    software: tuple[str, str, str, float],
    department: str,
    owner: str,
    purchased_licenses: int,
    assigned_licenses: int,
    days_until_renewal: int,
    reference: date,
    rng: np.random.Generator,
) -> dict:
    """Assemble a single software license record."""
    software_name, vendor, license_type, annual_cost = software
    available_licenses = purchased_licenses - assigned_licenses
    renewal_date = reference + timedelta(days=days_until_renewal)
    compliance_status = assign_compliance_status(
        purchased_licenses, assigned_licenses, days_until_renewal
    )
    cost_variance = float(rng.uniform(0.92, 1.08))

    return {
        "software_name": software_name,
        "vendor": vendor,
        "license_type": license_type,
        "purchased_licenses": purchased_licenses,
        "assigned_licenses": assigned_licenses,
        "available_licenses": available_licenses,
        "renewal_date": renewal_date,
        "days_until_renewal": days_until_renewal,
        "department": department,
        "owner": owner,
        "annual_cost": round(annual_cost * cost_variance, 2),
        "compliance_status": compliance_status,
    }


def _generate_scenario_record(
    index: int,
    scenario: dict,
    reference: date,
    rng: np.random.Generator,
    faker: Faker,
) -> dict:
    """Build a curated software license row."""
    software = SOFTWARE_CATALOG[index % len(SOFTWARE_CATALOG)]
    department = DEPARTMENTS[index % len(DEPARTMENTS)]
    owner = faker.name()

    return _build_record(
        index=index,
        software=software,
        department=department,
        owner=owner,
        purchased_licenses=scenario["purchased"],
        assigned_licenses=scenario["assigned"],
        days_until_renewal=scenario["days_until_renewal"],
        reference=reference,
        rng=rng,
    )


def _generate_random_record(
    index: int,
    reference: date,
    rng: np.random.Generator,
    faker: Faker,
) -> dict:
    """Generate a random software license record."""
    software = SOFTWARE_CATALOG[int(rng.integers(0, len(SOFTWARE_CATALOG)))]
    department = DEPARTMENTS[int(rng.integers(0, len(DEPARTMENTS)))]
    owner = faker.name()
    purchased = int(rng.integers(25, 400))
    assigned = int(rng.integers(10, purchased + 5))
    days_until_renewal = int(rng.integers(15, 365))

    return _build_record(
        index=index,
        software=software,
        department=department,
        owner=owner,
        purchased_licenses=purchased,
        assigned_licenses=assigned,
        days_until_renewal=days_until_renewal,
        reference=reference,
        rng=rng,
    )


def generate_software_data(
    row_count: int | None = None,
    seed: int | None = None,
) -> pd.DataFrame:
    """
    Build a DataFrame of fictional software license records.

    Args:
        row_count: Number of rows to generate. Defaults to ROW_COUNTS config.
        seed: Random seed for reproducibility. Defaults to RANDOM_SEED config.

    Returns:
        DataFrame with software license columns in sheet order.
    """
    row_count = row_count or ROW_COUNTS["software"]["default"]
    seed = seed if seed is not None else RANDOM_SEED
    reference = DEMO_REFERENCE_DATE

    rng = np.random.default_rng(seed)
    faker = Faker()
    Faker.seed(seed)

    records: list[dict] = []
    for i, scenario in enumerate(COMPLIANCE_SCENARIOS, start=1):
        records.append(_generate_scenario_record(i, scenario, reference, rng, faker))

    for i in range(len(COMPLIANCE_SCENARIOS) + 1, row_count + 1):
        records.append(_generate_random_record(i, reference, rng, faker))

    df = pd.DataFrame(records, columns=COLUMN_ORDER)

    # Re-apply compliance rules for consistency
    for idx in df.index:
        row = df.loc[idx]
        df.at[idx, "compliance_status"] = assign_compliance_status(
            int(row["purchased_licenses"]),
            int(row["assigned_licenses"]),
            int(row["days_until_renewal"]),
        )
        df.at[idx, "available_licenses"] = (
            int(row["purchased_licenses"]) - int(row["assigned_licenses"])
        )

    return df


def save_software_data(df: pd.DataFrame, output_dir: Path | None = None) -> Path:
    """Write software license data to CSV in data/generated/."""
    output_dir = output_dir or DATA_GENERATED_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / CSV_FILES["software"]
    df.to_csv(path, index=False, date_format="%Y-%m-%d")
    return path
