"""Demand forecasting — statistical methods, error metrics, and horizon projections."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable

import pandas as pd

from config.workbook_config import (
    FORECAST_BLEND_FORECAST_WEIGHT,
    FORECAST_HOLDOUT_WEEKS,
    FORECAST_MA_WINDOW,
    FORECAST_PRIMARY_METRIC,
    FORECAST_SES_ALPHA,
    FORECAST_WMA_WEIGHTS,
)

FORECAST_METHODS = (
    "Naive",
    "4-Week Moving Average",
    "Weighted Moving Average",
    "Simple Exponential Smoothing",
)

DEMAND_FORECAST_HEADERS = [
    "SKU",
    "Location ID",
    "Location Name",
    "Product Name",
    "Category",
    "Demand Pattern",
    "History Length (Weeks)",
    "Naive MAE",
    "Naive WAPE",
    "4-Week MA MAE",
    "4-Week MA WAPE",
    "WMA MAE",
    "WMA WAPE",
    "SES MAE",
    "SES WAPE",
    "Selected Method",
    "Selected MAE",
    "Selected RMSE",
    "Selected WAPE",
    "Selected MAPE",
    "Forecast Bias",
    "Forecast 4-Week",
    "Forecast 8-Week",
    "Forecast 12-Week",
    "Avg Weekly Demand",
    "Demand Trend",
    "Stockout Constrained History",
    "Review Status",
    "Notes",
]


@dataclass(frozen=True)
class ForecastErrors:
    mae: float
    rmse: float
    wape: float
    mape: float | None
    bias: float


@dataclass(frozen=True)
class ForecastResult:
    method: str
    errors: ForecastErrors
    weekly_level: float
    forecast_4w: int
    forecast_8w: int
    forecast_12w: int


def _finite(value: float, default: float = 0.0) -> float:
    if not math.isfinite(value):
        return default
    return value


def _safe_div(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0 or not math.isfinite(denominator):
        return default
    result = numerator / denominator
    return _finite(result, default)


def _weekly_series(demand: pd.DataFrame, sku: str, location_id: str) -> list[float]:
    if demand.empty:
        return []
    subset = demand[(demand["sku"] == sku) & (demand["location_id"] == location_id)]
    if subset.empty:
        return []
    values = subset.sort_values("week_start_date")["units_sold"].astype(float).tolist()
    return [float(v) for v in values]


def _classify_demand_pattern(weekly: list[float], avg_daily: float, cv: float) -> str:
    if avg_daily <= 0:
        return "no_recent_demand"
    recent = weekly[-13:] if len(weekly) >= 13 else weekly
    if sum(recent) == 0:
        return "no_recent_demand"
    if cv >= 1.0:
        return "intermittent"
    if cv >= 0.5:
        return "seasonal"
    if len(weekly) >= 26:
        first = sum(weekly[:26]) / 26
        second = sum(weekly[26:]) / max(len(weekly[26:]), 1)
        if second > first * 1.15:
            return "trending"
        if second < first * 0.85:
            return "declining"
    if max(weekly) >= avg_daily * 7 * 2.5:
        return "promotional"
    return "stable"


def _demand_trend(weekly: list[float]) -> str:
    if len(weekly) < 8:
        return "Insufficient History"
    first = sum(weekly[: len(weekly) // 2]) / max(len(weekly) // 2, 1)
    second = sum(weekly[len(weekly) // 2 :]) / max(len(weekly) - len(weekly) // 2, 1)
    if second > first * 1.1:
        return "Increasing"
    if second < first * 0.9:
        return "Decreasing"
    return "Stable"


def _forecast_naive(history: list[float], steps: int) -> list[float]:
    level = history[-1] if history else 0.0
    return [max(0.0, level)] * steps


def _forecast_ma(history: list[float], steps: int) -> list[float]:
    window = history[-FORECAST_MA_WINDOW:] if history else []
    if not window:
        return [0.0] * steps
    level = sum(window) / len(window)
    return [max(0.0, level)] * steps


def _forecast_wma(history: list[float], steps: int) -> list[float]:
    weights = FORECAST_WMA_WEIGHTS
    window = history[-len(weights) :] if history else []
    if not window:
        return [0.0] * steps
    use_weights = weights[-len(window) :]
    weight_sum = sum(use_weights)
    level = (
        sum(v * w for v, w in zip(window, use_weights, strict=False)) / weight_sum
        if weight_sum
        else 0.0
    )
    return [max(0.0, level)] * steps


def _forecast_ses(history: list[float], steps: int) -> list[float]:
    if not history:
        return [0.0] * steps
    level = history[0]
    alpha = FORECAST_SES_ALPHA
    for value in history[1:]:
        level = alpha * value + (1 - alpha) * level
    return [max(0.0, level)] * steps


METHOD_FUNCTIONS: dict[str, Callable[[list[float], int], list[float]]] = {
    "Naive": _forecast_naive,
    "4-Week Moving Average": _forecast_ma,
    "Weighted Moving Average": _forecast_wma,
    "Simple Exponential Smoothing": _forecast_ses,
}


def _compute_errors(actuals: list[float], forecasts: list[float]) -> ForecastErrors:
    if not actuals or not forecasts or len(actuals) != len(forecasts):
        return ForecastErrors(0.0, 0.0, 0.0, None, 0.0)

    errors = [f - a for a, f in zip(actuals, forecasts, strict=False)]
    abs_errors = [abs(e) for e in errors]
    mae = _finite(sum(abs_errors) / len(abs_errors))
    rmse = _finite(math.sqrt(sum(e * e for e in errors) / len(errors)))
    actual_sum = sum(abs(a) for a in actuals)
    wape = _finite(sum(abs_errors) / actual_sum) if actual_sum > 0 else 0.0

    mape_values = [
        abs(a - f) / abs(a) for a, f in zip(actuals, forecasts, strict=False) if a != 0
    ]
    mape = _finite(sum(mape_values) / len(mape_values)) if mape_values else None

    actual_mean = sum(actuals) / len(actuals)
    bias = _safe_div(sum(errors), actual_mean) if actual_mean != 0 else sum(errors)
    return ForecastErrors(
        mae=round(mae, 4),
        rmse=round(rmse, 4),
        wape=round(wape, 4),
        mape=round(mape, 4) if mape is not None else None,
        bias=round(bias, 4),
    )


def evaluate_method_holdout(
    history: list[float],
    method_fn: Callable[[list[float], int], list[float]],
    holdout_weeks: int = FORECAST_HOLDOUT_WEEKS,
) -> ForecastErrors:
    """One-step rolling holdout evaluation."""
    if len(history) <= holdout_weeks:
        return ForecastErrors(0.0, 0.0, 0.0, None, 0.0)

    actuals: list[float] = []
    forecasts: list[float] = []
    start = len(history) - holdout_weeks
    for idx in range(start, len(history)):
        train = history[:idx]
        pred = method_fn(train, 1)[0]
        actuals.append(history[idx])
        forecasts.append(pred)
    return _compute_errors(actuals, forecasts)


def select_best_method(
    history: list[float], holdout_weeks: int = FORECAST_HOLDOUT_WEEKS
) -> tuple[str, ForecastErrors]:
    """Select method with lowest WAPE on holdout (primary metric)."""
    best_method = "Naive"
    best_errors = ForecastErrors(0.0, 0.0, float("inf"), None, 0.0)
    best_mae = float("inf")

    for name, fn in METHOD_FUNCTIONS.items():
        errors = evaluate_method_holdout(history, fn, holdout_weeks)
        if errors.wape < best_errors.wape or (
            errors.wape == best_errors.wape and errors.mae < best_mae
        ):
            best_method = name
            best_errors = errors
            best_mae = errors.mae

    if not math.isfinite(best_errors.wape):
        best_errors = ForecastErrors(0.0, 0.0, 0.0, None, 0.0)
    return best_method, best_errors


def project_horizons(history: list[float], method: str) -> ForecastResult:
    """Project 4-, 8-, and 12-week totals using the selected method."""
    fn = METHOD_FUNCTIONS[method]
    weekly = fn(history, 1)[0] if history else 0.0
    weekly = max(0.0, _finite(weekly))
    return ForecastResult(
        method=method,
        errors=ForecastErrors(0.0, 0.0, 0.0, None, 0.0),
        weekly_level=round(weekly, 4),
        forecast_4w=int(round(weekly * 4)),
        forecast_8w=int(round(weekly * 8)),
        forecast_12w=int(round(weekly * 12)),
    )


def forecast_sku_location(
    history: list[float], holdout_weeks: int = FORECAST_HOLDOUT_WEEKS
) -> dict[str, Any]:
    """Full forecast package for one SKU-location series."""
    if not history:
        empty_errors = ForecastErrors(0.0, 0.0, 0.0, None, 0.0)
        return {
            "method_errors": {name: empty_errors for name in FORECAST_METHODS},
            "selected_method": "Naive",
            "selected_errors": empty_errors,
            "weekly_level": 0.0,
            "forecast_4w": 0,
            "forecast_8w": 0,
            "forecast_12w": 0,
        }

    method_errors: dict[str, ForecastErrors] = {}
    for name, fn in METHOD_FUNCTIONS.items():
        method_errors[name] = evaluate_method_holdout(history, fn, holdout_weeks)

    selected_method, selected_errors = select_best_method(history, holdout_weeks)
    projection = project_horizons(history, selected_method)
    projection = ForecastResult(
        method=selected_method,
        errors=selected_errors,
        weekly_level=projection.weekly_level,
        forecast_4w=projection.forecast_4w,
        forecast_8w=projection.forecast_8w,
        forecast_12w=projection.forecast_12w,
    )

    return {
        "method_errors": method_errors,
        "selected_method": selected_method,
        "selected_errors": selected_errors,
        "weekly_level": projection.weekly_level,
        "forecast_4w": projection.forecast_4w,
        "forecast_8w": projection.forecast_8w,
        "forecast_12w": projection.forecast_12w,
    }


def resolve_planning_demand(
    historical_avg_daily: float,
    forecast_weekly_level: float,
    selected_wape: float,
    historical_wape: float,
) -> tuple[float, str]:
    """Choose planning demand source for replenishment integration."""
    historical_avg_daily = max(0.0, historical_avg_daily)
    forecast_daily = max(0.0, forecast_weekly_level / 7.0)

    if forecast_weekly_level <= 0 and historical_avg_daily <= 0:
        return 0.0, "Historical Average"
    if forecast_weekly_level <= 0:
        return historical_avg_daily, "Historical Average"
    if historical_avg_daily <= 0:
        return forecast_daily, "Selected Forecast"

    if selected_wape < historical_wape and selected_wape < historical_wape * 0.90:
        blended = (
            FORECAST_BLEND_FORECAST_WEIGHT * forecast_daily
            + (1 - FORECAST_BLEND_FORECAST_WEIGHT) * historical_avg_daily
        )
        return round(blended, 4), "Blended Demand"
    if selected_wape <= historical_wape:
        return forecast_daily, "Selected Forecast"
    return historical_avg_daily, "Historical Average"


def _normalize_inventory(inventory: pd.DataFrame) -> pd.DataFrame:
    if inventory.empty:
        return inventory
    inv = inventory.copy()
    if "location_name" not in inv.columns:
        inv["location_name"] = inv.get("location", "")
    if "location_id" not in inv.columns:
        inv["location_id"] = inv.get("location", inv.get("location_name", "UNKNOWN"))
    return inv


def build_demand_forecast_dataframe(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build demand forecast table for all SKU-locations with demand history."""
    inventory = _normalize_inventory(
        data.get("inventory_full", data.get("inventory", pd.DataFrame()))
    )
    demand = data.get("demand_history", pd.DataFrame())

    if inventory.empty or demand.empty:
        return pd.DataFrame(columns=DEMAND_FORECAST_HEADERS)

    sku_locations = demand[["sku", "location_id"]].drop_duplicates()
    meta = inventory.drop_duplicates(subset=["sku", "location_id"]).set_index(
        ["sku", "location_id"]
    )

    rows: list[dict[str, Any]] = []
    for _, key in sku_locations.iterrows():
        sku = key["sku"]
        loc_id = key["location_id"]
        weekly = _weekly_series(demand, sku, loc_id)
        history_len = len(weekly)
        avg_weekly = sum(weekly) / history_len if history_len else 0.0
        avg_daily = avg_weekly / 7.0
        if history_len > 1:
            var_w = sum((w - avg_weekly) ** 2 for w in weekly) / history_len
            cv = _safe_div(math.sqrt(var_w), avg_weekly)
        else:
            cv = 0.0
        pattern = _classify_demand_pattern(weekly, avg_daily, cv)

        subset = demand[(demand["sku"] == sku) & (demand["location_id"] == loc_id)]
        stockout_weeks = int((subset["stockout_flag"] == "Yes").sum())

        forecast = forecast_sku_location(weekly)
        method_errors = forecast["method_errors"]
        selected = forecast["selected_errors"]

        if history_len < FORECAST_HOLDOUT_WEEKS + 4:
            review = "Limited History"
            notes = f"Holdout requires {FORECAST_HOLDOUT_WEEKS} weeks; review manually"
        elif pattern == "no_recent_demand":
            review = "No Recent Demand"
            notes = "Zero recent demand; forecasts default to zero"
        elif selected.wape > 0.5:
            review = "High Error"
            notes = f"Selected {FORECAST_PRIMARY_METRIC} exceeds 50%; validate inputs"
        else:
            review = "Approved"
            notes = f"Best method selected by lowest holdout {FORECAST_PRIMARY_METRIC}"

        inv = meta.loc[(sku, loc_id)] if (sku, loc_id) in meta.index else None

        row: dict[str, Any] = {
            "SKU": sku,
            "Location ID": loc_id,
            "Location Name": inv["location_name"] if inv is not None else "",
            "Product Name": inv["product_name"] if inv is not None else "",
            "Category": inv["category"] if inv is not None else "",
            "Demand Pattern": pattern,
            "History Length (Weeks)": history_len,
            "Naive MAE": method_errors["Naive"].mae,
            "Naive WAPE": method_errors["Naive"].wape,
            "4-Week MA MAE": method_errors["4-Week Moving Average"].mae,
            "4-Week MA WAPE": method_errors["4-Week Moving Average"].wape,
            "WMA MAE": method_errors["Weighted Moving Average"].mae,
            "WMA WAPE": method_errors["Weighted Moving Average"].wape,
            "SES MAE": method_errors["Simple Exponential Smoothing"].mae,
            "SES WAPE": method_errors["Simple Exponential Smoothing"].wape,
            "Selected Method": forecast["selected_method"],
            "Selected MAE": selected.mae,
            "Selected RMSE": selected.rmse,
            "Selected WAPE": selected.wape,
            "Selected MAPE": selected.mape,
            "Forecast Bias": selected.bias,
            "Forecast 4-Week": forecast["forecast_4w"],
            "Forecast 8-Week": forecast["forecast_8w"],
            "Forecast 12-Week": forecast["forecast_12w"],
            "Avg Weekly Demand": round(avg_weekly, 4),
            "Demand Trend": _demand_trend(weekly),
            "Stockout Constrained History": stockout_weeks,
            "Review Status": review,
            "Notes": notes,
        }
        rows.append(row)

    return pd.DataFrame(rows, columns=DEMAND_FORECAST_HEADERS)


def build_forecast_lookup(
    data: dict[str, pd.DataFrame],
) -> dict[tuple[str, str], dict[str, Any]]:
    """Lookup table for replenishment integration."""
    df = build_demand_forecast_dataframe(data)
    lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for _, row in df.iterrows():
        key = (str(row["SKU"]), str(row["Location ID"]))
        lookup[key] = {
            "weekly_level": _safe_div(float(row["Forecast 4-Week"]), 4.0),
            "selected_wape": float(row["Selected WAPE"]),
            "historical_wape": float(row["Naive WAPE"]),
            "selected_method": str(row["Selected Method"]),
        }
    return lookup


def select_demo_chart_skus(df: pd.DataFrame, count: int = 3) -> list[str]:
    """Pick demonstration SKUs with varied demand for charts."""
    if df.empty:
        return []
    ranked = df.sort_values("Forecast 12-Week", ascending=False)
    picks: list[str] = []
    for pattern in ("stable", "trending", "seasonal", "intermittent"):
        match = ranked[ranked["Demand Pattern"] == pattern]
        if not match.empty:
            sku = str(match.iloc[0]["SKU"])
            if sku not in picks:
                picks.append(sku)
        if len(picks) >= count:
            break
    for _, row in ranked.iterrows():
        sku = str(row["SKU"])
        if sku not in picks:
            picks.append(sku)
        if len(picks) >= count:
            break
    return picks[:count]
