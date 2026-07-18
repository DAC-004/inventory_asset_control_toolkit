"""ABC classification, turnover, DOH, accuracy, and cycle count analytics."""

from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Any

import pandas as pd

from config.workbook_config import (
    ABC_A_THRESHOLD,
    ABC_B_THRESHOLD,
    AS_OF_DATE,
    CYCLE_COUNT_FREQUENCY,
)

CLASSIFICATION_HEADERS = [
    "SKU",
    "Product Name",
    "Category",
    "Supplier ID",
    "Annual Units Sold",
    "Annualized COGS",
    "Annual Usage Value",
    "Value Rank",
    "Cumulative Usage Value",
    "Cumulative Usage %",
    "ABC Class",
    "Average Inventory Value",
    "Inventory Turnover",
    "Financial DOH",
    "DOH Status",
    "Avg Daily Demand",
    "Unit Coverage Days",
    "Coverage Status",
    "Unit Accuracy %",
    "Exact Match Rate",
    "Variance Units",
    "Variance Value",
    "High-Value Variance Count",
    "Last Count Date",
    "Next Count Due",
    "Count Frequency",
    "Count Priority",
    "Count Status",
]

CYCLE_COUNT_PLAN_HEADERS = [
    "Count Priority",
    "SKU",
    "Location ID",
    "Location Name",
    "Product Name",
    "ABC Class",
    "System Quantity",
    "Unit Cost",
    "Inventory Value",
    "Last Count Date",
    "Next Count Due",
    "Days Until Due",
    "Count Frequency",
    "Prior Variance Units",
    "Unit Accuracy %",
    "Risk Score",
    "Count Status",
    "Assigned Counter",
    "Notes",
]

HIGH_VALUE_VARIANCE_THRESHOLD = 500.0


def validate_abc_thresholds(
    a_threshold: float = ABC_A_THRESHOLD,
    b_threshold: float = ABC_B_THRESHOLD,
) -> None:
    """Ensure 0 < A < B < 1."""
    if not (0 < a_threshold < b_threshold < 1):
        raise ValueError(
            f"ABC thresholds must satisfy 0 < A < B < 1; got A={a_threshold}, B={b_threshold}"
        )


def _safe_div(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0 or not math.isfinite(denominator):
        return default
    result = numerator / denominator
    if not math.isfinite(result):
        return default
    return result


def _assign_abc_class(cumulative_pct: float) -> str:
    """Assign ABC class using inclusive cumulative percentage boundaries."""
    validate_abc_thresholds()
    if cumulative_pct <= ABC_A_THRESHOLD:
        return "A"
    if cumulative_pct <= ABC_B_THRESHOLD:
        return "B"
    return "C"


def _trailing_52_week_units(demand: pd.DataFrame) -> pd.Series:
    """Sum units sold by SKU over demand history (52 weeks)."""
    if demand.empty:
        return pd.Series(dtype=float)
    return demand.groupby("sku")["units_sold"].sum()


def _sku_unit_costs(inventory: pd.DataFrame) -> pd.Series:
    return inventory.groupby("sku")["unit_cost"].mean()


def _compute_abc_table(demand: pd.DataFrame, inventory: pd.DataFrame) -> pd.DataFrame:
    """Enterprise SKU ABC table with rank and cumulative usage value."""
    units = _trailing_52_week_units(demand)
    costs = _sku_unit_costs(inventory)
    skus = sorted(set(units.index) | set(costs.index))

    rows = []
    for sku in skus:
        annual_units = float(units.get(sku, 0))
        unit_cost = float(costs.get(sku, 0))
        usage_value = round(annual_units * unit_cost, 2)
        rows.append(
            {
                "sku": sku,
                "annual_units_sold": int(round(annual_units)),
                "annualized_cogs": usage_value,
                "annual_usage_value": usage_value,
            }
        )

    abc = pd.DataFrame(rows)
    if abc.empty:
        return abc

    abc = abc.sort_values("annual_usage_value", ascending=False).reset_index(drop=True)
    abc["value_rank"] = abc.index + 1
    total_usage = abc["annual_usage_value"].sum()
    if total_usage > 0:
        abc["cumulative_usage_value"] = abc["annual_usage_value"].cumsum().round(2)
        abc["cumulative_usage_pct"] = (
            abc["cumulative_usage_value"] / total_usage
        ).round(4)
    else:
        abc["cumulative_usage_value"] = 0.0
        abc["cumulative_usage_pct"] = 0.0
    abc["abc_class"] = abc["cumulative_usage_pct"].map(_assign_abc_class)
    return abc


def _average_inventory_by_sku(snapshots: pd.DataFrame) -> pd.Series:
    if snapshots.empty:
        return pd.Series(dtype=float)
    monthly = (
        snapshots.groupby(["sku", "snapshot_date"])["inventory_value"]
        .sum()
        .reset_index()
    )
    return monthly.groupby("sku")["inventory_value"].mean()


def _compute_turnover(annualized_cogs: float, avg_inventory_value: float) -> float:
    return round(_safe_div(annualized_cogs, avg_inventory_value, 0.0), 4)


def _financial_doh(turnover: float) -> tuple[float | None, str]:
    if turnover <= 0:
        return None, "No Demand"
    doh = round(_safe_div(365.0, turnover, 0.0), 1)
    if doh <= 0 or not math.isfinite(doh):
        return None, "No Demand"
    return doh, "Calculated"


def _unit_coverage_days(
    qoh: float, avg_daily_demand: float
) -> tuple[float | None, str]:
    if avg_daily_demand <= 0:
        return None, "No Demand"
    days = round(_safe_div(qoh, avg_daily_demand, 0.0), 1)
    return days, "Calculated"


def _accuracy_metrics(counts: pd.DataFrame) -> dict[str, float | int]:
    if counts.empty:
        return {
            "unit_accuracy_pct": 1.0,
            "exact_match_rate": 1.0,
            "variance_units": 0,
            "variance_value": 0.0,
            "high_value_variance_count": 0,
        }
    completed = counts[counts["count_status"].isin(["Completed", "Recount Required"])]
    if completed.empty:
        completed = counts

    accuracies = []
    exact = 0
    for _, row in completed.iterrows():
        system_q = int(row["system_quantity"])
        physical_q = int(row["physical_quantity"])
        denom = max(system_q, physical_q, 1)
        acc = max(0.0, min(1.0, 1.0 - abs(physical_q - system_q) / denom))
        accuracies.append(acc)
        if system_q == physical_q:
            exact += 1

    return {
        "unit_accuracy_pct": round(sum(accuracies) / len(accuracies), 4),
        "exact_match_rate": round(exact / len(completed), 4),
        "variance_units": int(completed["variance_units"].abs().sum()),
        "variance_value": round(completed["variance_value"].abs().sum(), 2),
        "high_value_variance_count": int(
            (completed["variance_value"].abs() >= HIGH_VALUE_VARIANCE_THRESHOLD).sum()
        ),
    }


def _accuracy_by_sku_location(counts: pd.DataFrame) -> pd.DataFrame:
    if counts.empty:
        return pd.DataFrame(
            columns=["sku", "location_id", "unit_accuracy_pct", "prior_variance_units"]
        )
    rows = []
    for (sku, loc), grp in counts.groupby(["sku", "location_id"]):
        metrics = _accuracy_metrics(grp)
        prior_var = int(grp.sort_values("scheduled_date")["variance_units"].iloc[-1])
        rows.append(
            {
                "sku": sku,
                "location_id": loc,
                "unit_accuracy_pct": metrics["unit_accuracy_pct"],
                "prior_variance_units": prior_var,
            }
        )
    return pd.DataFrame(rows)


def _next_count_due(last_count: date | None, abc_class: str) -> date:
    freq = CYCLE_COUNT_FREQUENCY.get(abc_class, "Semiannually")
    days_map = {"Monthly": 30, "Quarterly": 91, "Semiannually": 182}
    interval = days_map.get(freq, 182)
    base = last_count or (AS_OF_DATE - timedelta(days=interval))
    return base + timedelta(days=interval)


def _count_status(next_due: date, last_status: str | None) -> str:
    if last_status == "Recount Required":
        return "Recount Required"
    if last_status == "Completed":
        return "Completed"
    days_until = (next_due - AS_OF_DATE).days
    if days_until < 0:
        return "Overdue"
    if days_until == 0:
        return "Due"
    if days_until <= 7:
        return "Due Soon"
    return "Scheduled"


def _risk_score(
    abc_class: str,
    unit_cost: float,
    prior_variance: int,
    transaction_volume: int,
    stockout_risk: bool,
    count_status: str,
) -> int:
    score = 0.0
    score += {"A": 30, "B": 20, "C": 10}.get(abc_class, 10)
    score += min(unit_cost / 10.0, 25)
    score += min(abs(prior_variance) * 2, 20)
    score += min(transaction_volume / 2.0, 15)
    if stockout_risk:
        score += 10
    if count_status == "Overdue":
        score += 15
    elif count_status == "Due":
        score += 10
    elif count_status == "Due Soon":
        score += 5
    return int(min(round(score), 100))


def build_classification_dataframe(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build enterprise SKU classification table."""
    inventory = data.get("inventory_full", data.get("inventory", pd.DataFrame()))
    if "location_name" not in inventory.columns and "location" in inventory.columns:
        inventory = inventory.copy()
        inventory["location_name"] = inventory["location"]

    demand = data.get("demand_history", pd.DataFrame())
    snapshots = data.get("inventory_snapshots", pd.DataFrame())
    counts = data.get("cycle_counts", pd.DataFrame())

    abc = _compute_abc_table(demand, inventory)
    if abc.empty:
        return pd.DataFrame(columns=CLASSIFICATION_HEADERS)

    avg_inv = _average_inventory_by_sku(snapshots)
    agg_spec: dict[str, tuple[str, str]] = {
        "product_name": ("product_name", "first"),
        "category": ("category", "first"),
        "quantity_on_hand": ("quantity_on_hand", "sum"),
        "demand_90_day": ("demand_90_day", "sum"),
    }
    if "supplier_id" in inventory.columns:
        agg_spec["supplier_id"] = ("supplier_id", "first")
    inv_meta = inventory.groupby("sku").agg(**agg_spec)
    rows = []
    for _, row in abc.iterrows():
        sku = row["sku"]
        meta = inv_meta.loc[sku] if sku in inv_meta.index else None
        avg_inventory = round(float(avg_inv.get(sku, 0)), 2)
        turnover = _compute_turnover(row["annualized_cogs"], avg_inventory)
        fin_doh, doh_status = _financial_doh(turnover)
        avg_daily = _safe_div(
            float(meta["demand_90_day"]) if meta is not None else 0, 90
        )
        coverage, cov_status = _unit_coverage_days(
            float(meta["quantity_on_hand"]) if meta is not None else 0, avg_daily
        )

        sku_counts = (
            counts[counts["sku"] == sku] if not counts.empty else pd.DataFrame()
        )
        sku_accuracy = _accuracy_metrics(sku_counts)
        last_count = (
            pd.to_datetime(sku_counts["count_date"]).max()
            if not sku_counts.empty and sku_counts["count_date"].notna().any()
            else pd.NaT
        )
        last_count_date = (
            last_count.date() if pd.notna(last_count) else None  # type: ignore[union-attr]
        )
        abc_class = row["abc_class"]
        next_due = _next_count_due(last_count_date, abc_class)
        count_status = _count_status(
            next_due,
            str(sku_counts["count_status"].iloc[-1]) if not sku_counts.empty else None,
        )
        priority = {"A": "High", "B": "Medium", "C": "Low"}.get(abc_class, "Low")

        rows.append(
            {
                "SKU": sku,
                "Product Name": meta["product_name"] if meta is not None else "",
                "Category": meta["category"] if meta is not None else "",
                "Supplier ID": (
                    meta["supplier_id"]
                    if meta is not None and "supplier_id" in meta.index
                    else ""
                ),
                "Annual Units Sold": int(row["annual_units_sold"]),
                "Annualized COGS": row["annualized_cogs"],
                "Annual Usage Value": row["annual_usage_value"],
                "Value Rank": int(row["value_rank"]),
                "Cumulative Usage Value": row["cumulative_usage_value"],
                "Cumulative Usage %": row["cumulative_usage_pct"],
                "ABC Class": abc_class,
                "Average Inventory Value": avg_inventory,
                "Inventory Turnover": turnover,
                "Financial DOH": fin_doh,
                "DOH Status": doh_status,
                "Avg Daily Demand": round(avg_daily, 2),
                "Unit Coverage Days": coverage,
                "Coverage Status": cov_status,
                "Unit Accuracy %": sku_accuracy["unit_accuracy_pct"],
                "Exact Match Rate": sku_accuracy["exact_match_rate"],
                "Variance Units": sku_accuracy["variance_units"],
                "Variance Value": sku_accuracy["variance_value"],
                "High-Value Variance Count": sku_accuracy["high_value_variance_count"],
                "Last Count Date": last_count_date,
                "Next Count Due": next_due,
                "Count Frequency": CYCLE_COUNT_FREQUENCY[abc_class],
                "Count Priority": priority,
                "Count Status": count_status,
            }
        )

    return pd.DataFrame(rows, columns=CLASSIFICATION_HEADERS)


def build_cycle_count_plan_dataframe(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build SKU-location cycle count plan sorted by risk and overdue status."""
    inventory = data.get("inventory_full", data.get("inventory", pd.DataFrame()))
    counts = data.get("cycle_counts", pd.DataFrame())
    demand = data.get("demand_history", pd.DataFrame())
    classification = build_classification_dataframe(data)
    abc_map = classification.set_index("SKU")["ABC Class"].to_dict()
    acc_map = _accuracy_by_sku_location(counts)

    if inventory.empty:
        return pd.DataFrame(columns=CYCLE_COUNT_PLAN_HEADERS)

    if "location_name" not in inventory.columns:
        inventory = inventory.copy()
        inventory["location_name"] = inventory.get("location", "")

    if "location_id" not in inventory.columns:
        inventory = inventory.copy()
        inventory["location_id"] = inventory.get(
            "location", inventory.get("location_name", "UNKNOWN")
        )

    txn_volume = (
        demand.groupby(["sku", "location_id"])["units_sold"].sum()
        if not demand.empty
        else pd.Series(dtype=float)
    )

    rows = []
    priority = 1
    for _, inv in inventory.iterrows():
        sku = inv["sku"]
        loc_id = inv["location_id"]
        abc_class = abc_map.get(sku, "C")
        loc_counts = (
            counts[(counts["sku"] == sku) & (counts["location_id"] == loc_id)]
            if not counts.empty
            else pd.DataFrame()
        )

        last_count = pd.NaT
        prior_var = 0
        assigned = ""
        notes = ""
        last_status = None
        if not loc_counts.empty:
            last_row = loc_counts.sort_values("scheduled_date").iloc[-1]
            last_count = pd.to_datetime(last_row["count_date"], errors="coerce")
            if pd.isna(last_count):
                last_count = pd.to_datetime(last_row["scheduled_date"], errors="coerce")
            prior_var = int(last_row["variance_units"])
            assigned = str(last_row.get("counter_name", ""))
            notes = str(last_row.get("root_cause", "") or "")
            last_status = str(last_row["count_status"])

        last_count_date = last_count.date() if pd.notna(last_count) else None
        next_due = _next_count_due(last_count_date, abc_class)
        status = _count_status(next_due, last_status)
        days_until = (next_due - AS_OF_DATE).days

        acc_row = (
            acc_map[(acc_map["sku"] == sku) & (acc_map["location_id"] == loc_id)]
            if not acc_map.empty
            else pd.DataFrame()
        )
        unit_acc = (
            float(acc_row["unit_accuracy_pct"].iloc[0]) if not acc_row.empty else 1.0
        )

        txn_key = (sku, loc_id)
        volume = int(txn_volume.get(txn_key, 0)) if len(txn_volume) else 0
        stockout = str(inv.get("status", "")) == "Stockout Risk"
        unit_cost = float(inv["unit_cost"])
        risk = _risk_score(abc_class, unit_cost, prior_var, volume, stockout, status)

        rows.append(
            {
                "Count Priority": priority,
                "SKU": sku,
                "Location ID": loc_id,
                "Location Name": inv["location_name"],
                "Product Name": inv["product_name"],
                "ABC Class": abc_class,
                "System Quantity": int(inv["quantity_on_hand"]),
                "Unit Cost": unit_cost,
                "Inventory Value": round(float(inv["quantity_on_hand"]) * unit_cost, 2),
                "Last Count Date": last_count_date,
                "Next Count Due": next_due,
                "Days Until Due": days_until,
                "Count Frequency": CYCLE_COUNT_FREQUENCY[abc_class],
                "Prior Variance Units": prior_var,
                "Unit Accuracy %": unit_acc,
                "Risk Score": risk,
                "Count Status": status,
                "Assigned Counter": assigned,
                "Notes": notes,
                "_sort_overdue": 0 if status == "Overdue" else 1,
                "_sort_risk": risk,
            }
        )
        priority += 1

    plan = pd.DataFrame(rows)
    if plan.empty:
        return pd.DataFrame(columns=CYCLE_COUNT_PLAN_HEADERS)

    plan = plan.sort_values(
        ["_sort_overdue", "_sort_risk"], ascending=[True, False]
    ).reset_index(drop=True)
    plan["Count Priority"] = plan.index + 1
    return plan[CYCLE_COUNT_PLAN_HEADERS]


def compute_turnover_summary(
    data: dict[str, pd.DataFrame],
) -> dict[str, float]:
    """Turnover at enterprise, category, location, and SKU levels."""
    inventory = data.get("inventory_full", data.get("inventory", pd.DataFrame()))
    demand = data.get("demand_history", pd.DataFrame())
    snapshots = data.get("inventory_snapshots", pd.DataFrame())
    results: dict[str, float] = {}

    units_by_sku = _trailing_52_week_units(demand)
    costs = _sku_unit_costs(inventory)
    total_cogs = sum(
        float(units_by_sku.get(s, 0)) * float(costs.get(s, 0))
        for s in units_by_sku.index
    )
    total_avg_inv = (
        float(snapshots["inventory_value"].sum())
        / max(snapshots["snapshot_date"].nunique(), 1)
        if not snapshots.empty
        else 0.0
    )
    results["enterprise"] = _compute_turnover(total_cogs, total_avg_inv)

    if not inventory.empty and "category" in inventory.columns:
        for cat in inventory["category"].unique():
            cat_skus = inventory.loc[inventory["category"] == cat, "sku"].unique()
            cat_cogs = sum(
                float(units_by_sku.get(s, 0)) * float(costs.get(s, 0)) for s in cat_skus
            )
            cat_snaps = (
                snapshots[snapshots["sku"].isin(cat_skus)]
                if not snapshots.empty
                else pd.DataFrame()
            )
            cat_avg = (
                float(cat_snaps["inventory_value"].sum())
                / max(cat_snaps["snapshot_date"].nunique(), 1)
                if not cat_snaps.empty
                else 0.0
            )
            results[f"category:{cat}"] = _compute_turnover(cat_cogs, cat_avg)

    if "location_id" in inventory.columns:
        for loc in inventory["location_id"].unique():
            loc_inv = inventory[inventory["location_id"] == loc]
            loc_skus = loc_inv["sku"].unique()
            loc_cogs = sum(
                float(units_by_sku.get(s, 0)) * float(costs.get(s, 0)) for s in loc_skus
            ) / max(len(loc_skus), 1)
            loc_snaps = (
                snapshots[snapshots["location_id"] == loc]
                if not snapshots.empty
                else pd.DataFrame()
            )
            loc_avg = (
                float(loc_snaps["inventory_value"].sum())
                / max(loc_snaps["snapshot_date"].nunique(), 1)
                if not loc_snaps.empty
                else 0.0
            )
            results[f"location:{loc}"] = _compute_turnover(loc_cogs, loc_avg)

    avg_inv_by_sku = _average_inventory_by_sku(snapshots)
    for sku in units_by_sku.index:
        cogs = float(units_by_sku.get(sku, 0)) * float(costs.get(sku, 0))
        results[f"sku:{sku}"] = _compute_turnover(
            cogs, float(avg_inv_by_sku.get(sku, 0))
        )

    return results


def compute_dashboard_classification_kpis(
    data: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    """KPI values for dashboard classification section."""
    classification = build_classification_dataframe(data)
    plan = build_cycle_count_plan_dataframe(data)
    turnover = compute_turnover_summary(data)

    abc_counts = (
        classification["ABC Class"].value_counts().to_dict()
        if not classification.empty
        else {}
    )
    overdue = int((plan["Count Status"] == "Overdue").sum()) if not plan.empty else 0

    fin_doh_vals = classification.loc[
        classification["DOH Status"] == "Calculated", "Financial DOH"
    ]
    cov_vals = classification.loc[
        classification["Coverage Status"] == "Calculated", "Unit Coverage Days"
    ]

    return {
        "abc_a_count": int(abc_counts.get("A", 0)),
        "abc_b_count": int(abc_counts.get("B", 0)),
        "abc_c_count": int(abc_counts.get("C", 0)),
        "enterprise_turnover": turnover.get("enterprise", 0.0),
        "avg_financial_doh": (
            round(float(fin_doh_vals.mean()), 1) if not fin_doh_vals.empty else 0.0
        ),
        "avg_coverage_days": (
            round(float(cov_vals.mean()), 1) if not cov_vals.empty else 0.0
        ),
        "avg_unit_accuracy_pct": (
            round(float(classification["Unit Accuracy %"].mean()), 4)
            if not classification.empty
            else 1.0
        ),
        "overdue_count": overdue,
    }
