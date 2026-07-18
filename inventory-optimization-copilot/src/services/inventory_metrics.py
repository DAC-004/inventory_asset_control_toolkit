"""Core inventory metric and status calculations."""

from __future__ import annotations

from config.workbook_config import INVENTORY_THRESHOLDS


def calc_sell_through_rate(quantity_on_hand: int, demand_90_day: int) -> float:
    """Sell-through = 90-day demand / (on-hand + demand), capped at 1.0."""
    denominator = quantity_on_hand + demand_90_day
    if denominator == 0:
        return 0.0
    return round(min(demand_90_day / denominator, 1.0), 4)


def calc_gross_margin_pct(unit_cost: float, selling_price: float) -> float:
    """Gross margin % = (Selling Price - Unit Cost) / Selling Price."""
    if selling_price <= 0:
        return 0.0
    return round((selling_price - unit_cost) / selling_price, 4)


def assign_status_and_action(
    quantity_on_hand: int,
    min_stock: int,
    max_stock: int,
    age_days: int,
    demand_90_day: int,
    sell_through_rate: float,
) -> tuple[str, str]:
    """
    Apply inventory business rules in priority order.

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

    if quantity_on_hand > max_stock and age_days > thresholds["excess_aged_age_days"]:
        return "Excess / Aged", "Transfer or Markdown"

    if quantity_on_hand > max_stock:
        return "Excess", "Review Transfer"

    if (
        age_days > thresholds["slow_moving_age_days"]
        and sell_through_rate < thresholds["slow_moving_sell_through_rate"]
    ):
        return "Slow-Moving", "Markdown Review"

    return "Healthy", "Monitor"
