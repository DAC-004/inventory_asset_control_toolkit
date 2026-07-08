"""KPI calculation functions."""

from __future__ import annotations

import numpy as np

from src.config.constants import DAYS_OF_SUPPLY_CAP
from src.models.inventory import InventoryHealthRecord, InventoryRecord


def inventory_value(on_hand_qty: float, unit_cost: float) -> float:
    return on_hand_qty * unit_cost


def gross_margin(retail_price: float, unit_cost: float) -> float:
    return retail_price - unit_cost


def gross_margin_percent(retail_price: float, unit_cost: float) -> float:
    if retail_price == 0:
        return 0.0
    return (retail_price - unit_cost) / retail_price


def excess_qty(on_hand_qty: float, max_stock: float) -> float:
    return max(on_hand_qty - max_stock, 0)


def days_of_supply(on_hand_qty: float, avg_weekly_sales: float) -> float:
    if avg_weekly_sales == 0:
        return float(DAYS_OF_SUPPLY_CAP)
    avg_daily_sales = avg_weekly_sales / 7
    return on_hand_qty / avg_daily_sales


def sell_through_rate(demand_90_day: float, on_hand_qty: float) -> float:
    denominator = demand_90_day + on_hand_qty
    if denominator == 0:
        return 0.0
    return demand_90_day / denominator


def inventory_turnover(demand_90_day: float, unit_cost: float, inv_value: float) -> float:
    if inv_value == 0:
        return 0.0
    annualized_cogs = demand_90_day * 4 * unit_cost
    return annualized_cogs / inv_value


def gmroi(demand_90_day: float, gross_margin_dollars: float, inv_value: float) -> float:
    if inv_value == 0:
        return 0.0
    gross_margin_total = demand_90_day * gross_margin_dollars
    return gross_margin_total / inv_value


def compute_record_metrics(record: InventoryRecord) -> dict[str, float]:
    inv_value = inventory_value(record.on_hand_qty, record.unit_cost)
    gm = gross_margin(record.retail_price, record.unit_cost)
    return {
        "inventory_value": inv_value,
        "gross_margin": gm,
        "gross_margin_percent": gross_margin_percent(record.retail_price, record.unit_cost),
        "excess_qty": excess_qty(record.on_hand_qty, record.max_stock),
        "days_of_supply": days_of_supply(record.on_hand_qty, record.avg_weekly_sales),
        "sell_through_rate": sell_through_rate(record.demand_90_day, record.on_hand_qty),
        "inventory_turnover": inventory_turnover(
            record.demand_90_day, record.unit_cost, inv_value
        ),
        "gmroi": gmroi(record.demand_90_day, gm, inv_value),
    }


def average_days_of_supply(records: list[InventoryHealthRecord]) -> float:
    if not records:
        return 0.0
    values = [r.days_of_supply for r in records if r.days_of_supply < DAYS_OF_SUPPLY_CAP]
    if not values:
        return float(DAYS_OF_SUPPLY_CAP)
    return float(np.mean(values))
