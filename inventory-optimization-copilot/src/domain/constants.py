"""Shared domain constants for inventory optimization calculations."""

from __future__ import annotations

MARKDOWN_ACTIONS = ("Markdown Review", "Transfer or Markdown", "Liquidate")
TRANSFER_ACTIONS = ("Review Transfer", "Transfer or Markdown")

MARKDOWN_ELIGIBLE_STATUSES = ("Slow-Moving", "Excess / Aged", "Obsolete", "Excess")

TRANSFER_MARGIN_RATE = 0.35
TRANSFER_STRONG_DEMAND_THRESHOLD = 8

AGING_BUCKETS: list[tuple[str, int, int]] = [
    ("0-90 Days", 0, 90),
    ("91-180 Days", 91, 180),
    ("181-365 Days", 181, 365),
    ("365+ Days", 366, 99999),
]

RISK_LEVEL_ORDER = {"High": 0, "Medium": 1, "Low": 2}

ISSUE_TYPE_MAP = {
    "Stockout Risk": "Stockout Risk",
    "Obsolete": "Obsolete",
    "Excess / Aged": "Excess / Aged",
    "Excess": "Excess",
    "Slow-Moving": "Slow-Moving",
    "Healthy": "Within Target",
}

ANALYST_NOTES = {
    "Stockout Risk": "Below minimum stock — prioritize replenishment to avoid lost sales.",
    "Obsolete": "No 90-day demand and aged over 365 days — recommend liquidation review.",
    "Excess / Aged": "Over max stock with extended age — evaluate transfer before markdown.",
    "Excess": "Quantity exceeds max stock — consider transfer to locations with shortages.",
    "Slow-Moving": "Sell-through below 15% over 180+ days — review markdown options.",
    "Healthy": "Inventory levels and movement are within target range.",
}

DISPOSITION_SORT_ORDER = {
    "Liquidate": 0,
    "20% Markdown": 1,
    "10% Markdown": 2,
    "Transfer First": 3,
    "Hold": 4,
}

# Master Inventory column letters (for Excel formula KPIs)
MASTER_SHEET = "Master Inventory"
MASTER_DATA_START = 3
COL_TOTAL_VALUE = "N"
COL_AGE_DAYS = "Q"
COL_GROSS_MARGIN = "T"
COL_STATUS = "U"
COL_RECOMMENDED_ACTION = "V"
