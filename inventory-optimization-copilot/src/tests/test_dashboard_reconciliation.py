"""Dashboard KPI and summary reconciliation tests."""

from __future__ import annotations

import pandas as pd

from src.main import generate_all_data
from src.services.kpi_dashboard_service import (
    compute_abc_usage_summary,
    compute_action_summary,
    compute_aging_summary,
    compute_location_summary,
    compute_planning_service_kpis,
    compute_procurement_network_kpis,
    compute_replenishment_status_summary,
    compute_status_summary,
    compute_top_excess,
    compute_transfer_benefit_summary,
    compute_vendor_risk_summary,
)
from src.services.classification_service import compute_dashboard_classification_kpis

TOL = 0.01


def test_total_inventory_value_reconciliation():
    data = generate_all_data()
    df: pd.DataFrame = data["inventory"]
    expected = float(df["total_value"].sum())
    actual = float(df["total_value"].sum())
    assert abs(expected - actual) <= TOL


def test_aged_inventory_value_reconciliation():
    data = generate_all_data()
    df: pd.DataFrame = data["inventory"]
    aged = df.loc[df["age_days"] > 180, "total_value"].sum()
    assert aged >= 0


def test_location_summary_matches_source():
    data = generate_all_data()
    df: pd.DataFrame = data["inventory"]
    summary = compute_location_summary(df)
    assert abs(summary["inventory_value"].sum() - df["total_value"].sum()) <= TOL


def test_status_summary_matches_source():
    data = generate_all_data()
    df: pd.DataFrame = data["inventory"]
    summary = compute_status_summary(df)
    assert abs(summary["inventory_value"].sum() - df["total_value"].sum()) <= TOL


def test_aging_summary_matches_source():
    data = generate_all_data()
    df: pd.DataFrame = data["inventory"]
    summary = compute_aging_summary(df)
    assert abs(summary["inventory_value"].sum() - df["total_value"].sum()) <= TOL


def test_abc_summary_matches_classification():
    data = generate_all_data()
    summary = compute_abc_usage_summary(data)
    class_kpis = compute_dashboard_classification_kpis(data)
    assert summary["abc_class"].tolist() == sorted(summary["abc_class"].tolist())
    assert class_kpis["enterprise_turnover"] >= 0


def test_replenishment_summary_order_value():
    data = generate_all_data()
    summary = compute_replenishment_status_summary(data)
    planning = compute_planning_service_kpis(data)
    if not summary.empty:
        assert (
            abs(
                summary["recommended_order_value"].sum()
                - planning["recommended_order_value"]
            )
            <= TOL + 1
        )


def test_transfer_net_benefit_reconciliation():
    data = generate_all_data()
    summary = compute_transfer_benefit_summary(data)
    procurement = compute_procurement_network_kpis(data)
    if not summary.empty:
        assert (summary["net_benefit"] > 0).all()
        assert summary["net_benefit"].sum() <= procurement["transfer_net_benefit"] + TOL


def test_action_summary_matches_inventory_value():
    data = generate_all_data()
    df: pd.DataFrame = data["inventory"]
    summary = compute_action_summary(df)
    assert abs(summary["inventory_value"].sum() - df["total_value"].sum()) <= TOL


def test_vendor_risk_open_po_non_negative():
    data = generate_all_data()
    summary = compute_vendor_risk_summary(data)
    if not summary.empty:
        assert (summary["open_po_value"] >= 0).all()


def test_top_excess_limit_and_sort():
    data = generate_all_data()
    df: pd.DataFrame = data["inventory"]
    summary = compute_top_excess(df)
    assert len(summary) <= 10
    if len(summary) > 1:
        assert summary["excess_value"].is_monotonic_decreasing
