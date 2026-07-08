"""Inventory health classification and recommendation logic."""

from __future__ import annotations

from src.config.constants import (
    AGED_THRESHOLD_DAYS,
    HIGH_VALUE_THRESHOLD,
    MEDIUM_VALUE_THRESHOLD,
    OBSOLETE_AGE_DAYS,
    OBSOLETE_DEMAND_AGE_DAYS,
    SLOW_MOVING_DOS_THRESHOLD,
    SLOW_MOVING_SELL_THROUGH_THRESHOLD,
)
from src.models.inventory import InventoryHealthRecord, InventoryRecord
from src.services import kpi_service


def classify_inventory(records: list[InventoryRecord]) -> list[InventoryHealthRecord]:
    """Classify inventory records with health metrics and recommendations."""
    return [_classify_record(record) for record in records]


def _classify_record(record: InventoryRecord) -> InventoryHealthRecord:
    metrics = kpi_service.compute_record_metrics(record)

    aged_flag = record.inventory_age_days >= AGED_THRESHOLD_DAYS
    excess_flag = record.on_hand_qty > record.max_stock
    slow_moving_flag = (
        metrics["days_of_supply"] >= SLOW_MOVING_DOS_THRESHOLD
        and metrics["sell_through_rate"] < SLOW_MOVING_SELL_THROUGH_THRESHOLD
        and record.demand_90_day > 0
    )
    obsolete_flag = (
        record.discontinued_flag
        or record.inventory_age_days >= OBSOLETE_AGE_DAYS
        or (record.demand_90_day == 0 and record.inventory_age_days >= OBSOLETE_DEMAND_AGE_DAYS)
    )
    stockout_risk_flag = record.on_hand_qty < record.min_stock

    issue_type = _determine_issue_type(
        aged_flag, excess_flag, slow_moving_flag, obsolete_flag, stockout_risk_flag
    )
    risk_level = _determine_risk_level(
        issue_type, metrics["inventory_value"], record.inventory_age_days
    )
    recommended_action, reason = _determine_recommended_action(
        stockout_risk_flag,
        excess_flag,
        obsolete_flag,
        aged_flag,
        slow_moving_flag,
        issue_type,
    )

    return InventoryHealthRecord(
        **record.model_dump(),
        inventory_value=metrics["inventory_value"],
        gross_margin=metrics["gross_margin"],
        gross_margin_percent=metrics["gross_margin_percent"],
        excess_qty=metrics["excess_qty"],
        days_of_supply=metrics["days_of_supply"],
        sell_through_rate=metrics["sell_through_rate"],
        aged_flag=aged_flag,
        excess_flag=excess_flag,
        slow_moving_flag=slow_moving_flag,
        obsolete_flag=obsolete_flag,
        stockout_risk_flag=stockout_risk_flag,
        issue_type=issue_type,
        risk_level=risk_level,
        recommended_action=recommended_action,
        recommendation_reason=reason,
    )


def _determine_issue_type(
    aged_flag: bool,
    excess_flag: bool,
    slow_moving_flag: bool,
    obsolete_flag: bool,
    stockout_risk_flag: bool,
) -> str:
    if obsolete_flag:
        return "Obsolete"
    if excess_flag and aged_flag:
        return "Excess/Aged"
    if stockout_risk_flag:
        return "Stockout Risk"
    if excess_flag:
        return "Excess"
    if slow_moving_flag:
        return "Slow-Moving"
    if aged_flag:
        return "Aged"
    return "Healthy"


def _determine_risk_level(
    issue_type: str, inventory_value: float, inventory_age_days: int
) -> str:
    if (
        issue_type in {"Obsolete", "Excess/Aged"}
        or inventory_value >= HIGH_VALUE_THRESHOLD
        or inventory_age_days >= OBSOLETE_AGE_DAYS
    ):
        return "High"
    if issue_type in {"Excess", "Slow-Moving", "Aged", "Stockout Risk"} or inventory_value >= MEDIUM_VALUE_THRESHOLD:
        return "Medium"
    return "Low"


def _determine_recommended_action(
    stockout_risk_flag: bool,
    excess_flag: bool,
    obsolete_flag: bool,
    aged_flag: bool,
    slow_moving_flag: bool,
    issue_type: str,
) -> tuple[str, str]:
    if stockout_risk_flag:
        return (
            "Replenish",
            "On-hand quantity is below minimum stock threshold.",
        )
    if excess_flag and issue_type != "Obsolete":
        return (
            "Review Transfer or Markdown",
            "Location exceeds max stock; evaluate network transfer before markdown.",
        )
    if obsolete_flag and issue_type == "Obsolete":
        return (
            "Liquidate",
            "Item is obsolete with limited or no demand.",
        )
    if aged_flag or slow_moving_flag or excess_flag:
        return (
            "Review Markdown",
            "Aged or slow-moving inventory may require pricing action.",
        )
    return ("Monitor", "Inventory levels and demand are within acceptable ranges.")


def get_exception_records(records: list[InventoryHealthRecord]) -> list[InventoryHealthRecord]:
    """Return records that are not healthy."""
    return [r for r in records if r.issue_type != "Healthy"]
