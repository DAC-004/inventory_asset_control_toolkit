"""
Generate fictional inventory records for Master Inventory and related sheets.

Produces realistic auto-parts / shop-supply inventory for interview demos.
Output is deterministic when the same seed is used.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from config.workbook_config import (
    CSV_FILES,
    DATA_GENERATED_DIR,
    DEMO_REFERENCE_DATE,
    INVENTORY_THRESHOLDS,
    RANDOM_SEED,
    ROW_COUNTS,
)

# Column order matches Master Inventory sheet headers
COLUMN_ORDER = [
    "item_id",
    "sku",
    "product_name",
    "category",
    "subcategory",
    "location",
    "location_type",
    "region",
    "quantity_on_hand",
    "min_stock",
    "max_stock",
    "unit_cost",
    "selling_price",
    "total_value",
    "last_movement_date",
    "last_sale_date",
    "age_days",
    "demand_90_day",
    "sell_through_rate",
    "gross_margin_pct",
    "status",
    "recommended_action",
]

# (category, subcategory, product_name, unit_cost)
PRODUCT_CATALOG: list[tuple[str, str, str, float]] = [
    ("Tires", "All-Season", "Mavis Tour Plus 215/60R16", 89.99),
    ("Tires", "Performance", "Mavis Sport Grip 245/40R18", 124.50),
    ("Tires", "Winter", "Mavis SnowTrack 205/55R16", 98.75),
    ("Tires", "Commercial", "Mavis Fleet HD 225/75R16", 142.00),
    ("Brake Parts", "Pads", "Ceramic Brake Pad Set - Front", 34.25),
    ("Brake Parts", "Rotors", "Vented Brake Rotor 11.8in", 48.90),
    ("Brake Parts", "Calipers", "Reman Brake Caliper - Rear", 72.50),
    ("Brake Parts", "Hardware", "Brake Hardware Kit", 12.40),
    ("Batteries", "Automotive", "Mavis PowerStart 24F", 119.99),
    ("Batteries", "AGM", "Mavis AGM 47H6", 189.00),
    ("Batteries", "Marine", "Deep Cycle Marine 27DC", 145.50),
    ("Batteries", "Standard", "Economy Battery 35R", 89.00),
    ("Filters", "Oil", "Premium Oil Filter PF-2234", 8.75),
    ("Filters", "Air", "Engine Air Filter AF-9921", 14.20),
    ("Filters", "Cabin", "Cabin Air Filter CF-1180", 16.50),
    ("Filters", "Fuel", "Inline Fuel Filter FF-330", 11.90),
    ("Fluids", "Motor Oil", "Synthetic Motor Oil 5W-30 5qt", 28.99),
    ("Fluids", "Coolant", "Extended Life Coolant 1gal", 18.50),
    ("Fluids", "Brake Fluid", "DOT 4 Brake Fluid 12oz", 6.25),
    ("Fluids", "Transmission", "ATF+4 Transmission Fluid 1qt", 9.80),
    ("Tools", "Hand Tools", "3/8in Drive Socket Set 40pc", 54.00),
    ("Tools", "Diagnostic", "OBD-II Code Reader Pro", 129.00),
    ("Tools", "Power Tools", "Impact Wrench 1/2in 20V", 199.00),
    ("Tools", "Lifts", "Hydraulic Floor Jack 3-Ton", 165.00),
    ("Shop Supplies", "Cleaning", "Brake Cleaner 19oz", 5.50),
    ("Shop Supplies", "Safety", "Nitrile Gloves Box/100", 18.75),
    ("Shop Supplies", "Fasteners", "Assorted Clip & Retainer Kit", 22.40),
    ("Shop Supplies", "Lubricants", "Multi-Purpose Grease 14oz", 7.90),
    ("Accessories", "Wipers", "Beam Wiper Blade 22in", 19.99),
    ("Accessories", "Belts", "Serpentine Belt 6-Rib 68in", 24.50),
    ("Accessories", "Lighting", "LED Headlight Bulb H11 Pair", 39.00),
    ("Accessories", "Floor Mats", "All-Weather Floor Mat Set", 49.99),
]

LOCATIONS: list[tuple[str, str, str]] = [
    ("DC-NY", "Distribution Center", "Northeast"),
    ("DC-NJ", "Distribution Center", "Northeast"),
    ("DC-PA", "Distribution Center", "Northeast"),
    ("Store-Bronx", "Retail Store", "NYC Metro"),
    ("Store-Queens", "Retail Store", "NYC Metro"),
    ("Store-Brooklyn", "Retail Store", "NYC Metro"),
    ("Store-Manhattan", "Retail Store", "NYC Metro"),
    ("Store-WhitePlains", "Retail Store", "NYC Metro"),
    ("Store-Yonkers", "Retail Store", "NYC Metro"),
    ("Store-Newark", "Retail Store", "New Jersey"),
    ("Store-Stamford", "Retail Store", "Connecticut"),
]

# Curated rows — one per status (rules evaluated in priority order)
STATUS_SCENARIOS: list[dict] = [
    {
        "status": "Stockout Risk",
        "quantity_on_hand": 3,
        "min_stock": 12,
        "max_stock": 48,
        "age_days": 25,
        "demand_90_day": 18,
    },
    {
        "status": "Obsolete",
        "quantity_on_hand": 22,
        "min_stock": 8,
        "max_stock": 40,
        "age_days": 410,
        "demand_90_day": 0,
    },
    {
        "status": "Excess / Aged",
        "quantity_on_hand": 85,
        "min_stock": 10,
        "max_stock": 35,
        "age_days": 245,
        "demand_90_day": 6,
    },
    {
        "status": "Excess",
        "quantity_on_hand": 72,
        "min_stock": 10,
        "max_stock": 35,
        "age_days": 95,
        "demand_90_day": 14,
    },
    {
        "status": "Slow-Moving",
        "quantity_on_hand": 28,
        "min_stock": 10,
        "max_stock": 40,
        "age_days": 210,
        "demand_90_day": 2,
    },
    {
        "status": "Healthy",
        "quantity_on_hand": 24,
        "min_stock": 10,
        "max_stock": 45,
        "age_days": 40,
        "demand_90_day": 22,
    },
]


def assign_status_and_action(
    quantity_on_hand: int,
    min_stock: int,
    max_stock: int,
    age_days: int,
    demand_90_day: int,
    sell_through_rate: float,
) -> tuple[str, str]:
    """
    Apply inventory business rules in priority order (specs §7.1).

    Returns:
        (status, recommended_action) tuple.
    """
    thresholds = INVENTORY_THRESHOLDS

    if quantity_on_hand < min_stock:
        return "Stockout Risk", "Replenish"

    if (
        age_days > thresholds["obsolete_age_days"]
        and demand_90_day <= thresholds["zero_demand"]
    ):
        return "Obsolete", "Liquidate"

    if (
        quantity_on_hand > max_stock
        and age_days > thresholds["excess_aged_age_days"]
    ):
        return "Excess / Aged", "Transfer or Markdown"

    if quantity_on_hand > max_stock:
        return "Excess", "Review Transfer"

    if (
        age_days > thresholds["slow_moving_age_days"]
        and sell_through_rate < thresholds["slow_moving_sell_through_rate"]
    ):
        return "Slow-Moving", "Markdown Review"

    return "Healthy", "Monitor"


def _calc_sell_through_rate(quantity_on_hand: int, demand_90_day: int) -> float:
    """Sell-through = 90-day demand / (on-hand + demand), capped at 1.0."""
    denominator = quantity_on_hand + demand_90_day
    if denominator == 0:
        return 0.0
    return round(min(demand_90_day / denominator, 1.0), 4)


def _calc_gross_margin_pct(unit_cost: float, selling_price: float) -> float:
    """Gross margin % = (Selling Price - Unit Cost) / Selling Price."""
    if selling_price <= 0:
        return 0.0
    return round((selling_price - unit_cost) / selling_price, 4)


def _calc_dates_from_age(age_days: int, reference: date, rng: np.random.Generator) -> tuple[date, date]:
    """Derive last movement and last sale dates from age in days."""
    last_movement = reference - timedelta(days=int(age_days))
    # Last sale is same day or slightly more recent (within 14 days of movement)
    sale_offset = int(rng.integers(0, min(15, age_days + 1)))
    last_sale = reference - timedelta(days=max(0, age_days - sale_offset))
    return last_movement, last_sale


def _build_record(
    index: int,
    product: tuple[str, str, str, float],
    location: tuple[str, str, str],
    quantity_on_hand: int,
    min_stock: int,
    max_stock: int,
    age_days: int,
    demand_90_day: int,
    reference: date,
    rng: np.random.Generator,
    markup_range: tuple[float, float] = (1.35, 1.65),
) -> dict:
    """Assemble a single inventory record with derived fields."""
    category, subcategory, product_name, unit_cost = product
    location_name, location_type, region = location

    unit_cost = round(unit_cost * float(rng.uniform(0.95, 1.05)), 2)
    markup = float(rng.uniform(*markup_range))
    selling_price = round(unit_cost * markup, 2)
    total_value = round(quantity_on_hand * unit_cost, 2)
    sell_through_rate = _calc_sell_through_rate(quantity_on_hand, demand_90_day)
    gross_margin_pct = _calc_gross_margin_pct(unit_cost, selling_price)
    last_movement_date, last_sale_date = _calc_dates_from_age(age_days, reference, rng)
    status, recommended_action = assign_status_and_action(
        quantity_on_hand,
        min_stock,
        max_stock,
        age_days,
        demand_90_day,
        sell_through_rate,
    )

    sku_prefix = "".join(word[0] for word in category.split())[:2].upper()
    sku = f"{sku_prefix}-{1000 + index:04d}"

    return {
        "item_id": f"INV-{index:05d}",
        "sku": sku,
        "product_name": product_name,
        "category": category,
        "subcategory": subcategory,
        "location": location_name,
        "location_type": location_type,
        "region": region,
        "quantity_on_hand": quantity_on_hand,
        "min_stock": min_stock,
        "max_stock": max_stock,
        "unit_cost": unit_cost,
        "selling_price": selling_price,
        "total_value": total_value,
        "last_movement_date": last_movement_date,
        "last_sale_date": last_sale_date,
        "age_days": age_days,
        "demand_90_day": demand_90_day,
        "sell_through_rate": sell_through_rate,
        "gross_margin_pct": gross_margin_pct,
        "status": status,
        "recommended_action": recommended_action,
    }


def _generate_random_record(
    index: int,
    reference: date,
    rng: np.random.Generator,
) -> dict:
    """Generate a random inventory row with realistic field ranges."""
    product = PRODUCT_CATALOG[int(rng.integers(0, len(PRODUCT_CATALOG)))]
    location = LOCATIONS[int(rng.integers(0, len(LOCATIONS)))]

    min_stock = int(rng.integers(8, 21))
    max_stock = min_stock + int(rng.integers(15, 45))
    quantity_on_hand = int(rng.integers(0, max_stock + 35))
    age_days = int(rng.integers(5, 420))
    demand_90_day = int(rng.integers(0, 35))

    return _build_record(
        index=index,
        product=product,
        location=location,
        quantity_on_hand=quantity_on_hand,
        min_stock=min_stock,
        max_stock=max_stock,
        age_days=age_days,
        demand_90_day=demand_90_day,
        reference=reference,
        rng=rng,
    )


def _generate_scenario_record(
    index: int,
    scenario: dict,
    reference: date,
    rng: np.random.Generator,
) -> dict:
    """Generate a curated row designed to produce a specific inventory status."""
    product = PRODUCT_CATALOG[index % len(PRODUCT_CATALOG)]
    location = LOCATIONS[index % len(LOCATIONS)]

    return _build_record(
        index=index,
        product=product,
        location=location,
        quantity_on_hand=scenario["quantity_on_hand"],
        min_stock=scenario["min_stock"],
        max_stock=scenario["max_stock"],
        age_days=scenario["age_days"],
        demand_90_day=scenario["demand_90_day"],
        reference=reference,
        rng=rng,
    )


def generate_inventory_data(
    row_count: int | None = None,
    seed: int | None = None,
) -> pd.DataFrame:
    """
    Build a DataFrame of fictional inventory records.

    Args:
        row_count: Number of rows to generate. Defaults to ROW_COUNTS config.
        seed: Random seed for reproducibility. Defaults to RANDOM_SEED config.

    Returns:
        DataFrame with inventory columns in Master Inventory sheet order.
    """
    row_count = row_count or ROW_COUNTS["inventory"]["default"]
    seed = seed if seed is not None else RANDOM_SEED
    reference = DEMO_REFERENCE_DATE

    rng = np.random.default_rng(seed)
    reference = DEMO_REFERENCE_DATE

    records: list[dict] = []

    # Guaranteed examples of every status (first rows)
    for i, scenario in enumerate(STATUS_SCENARIOS, start=1):
        records.append(_generate_scenario_record(i, scenario, reference, rng))

    # Fill remaining rows with random realistic data
    for i in range(len(STATUS_SCENARIOS) + 1, row_count + 1):
        records.append(_generate_random_record(i, reference, rng))

    df = pd.DataFrame(records, columns=COLUMN_ORDER)

    # Re-apply rules to ensure consistency after any rounding
    for idx in df.index:
        row = df.loc[idx]
        status, action = assign_status_and_action(
            int(row["quantity_on_hand"]),
            int(row["min_stock"]),
            int(row["max_stock"]),
            int(row["age_days"]),
            int(row["demand_90_day"]),
            float(row["sell_through_rate"]),
        )
        df.at[idx, "status"] = status
        df.at[idx, "recommended_action"] = action

    return df


def save_inventory_data(df: pd.DataFrame, output_dir: Path | None = None) -> Path:
    """Write inventory data to CSV in data/generated/."""
    output_dir = output_dir or DATA_GENERATED_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / CSV_FILES["inventory"]
    df.to_csv(path, index=False, date_format="%Y-%m-%d")
    return path
