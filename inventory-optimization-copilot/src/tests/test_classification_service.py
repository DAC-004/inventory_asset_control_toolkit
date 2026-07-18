"""Tests for ABC classification, turnover, DOH, accuracy, and cycle counts."""

import math
from datetime import date, timedelta

import pytest

from config.workbook_config import ABC_A_THRESHOLD, ABC_B_THRESHOLD, AS_OF_DATE
from src.main import generate_all_data
from src.services.classification_service import (
    CLASSIFICATION_HEADERS,
    CYCLE_COUNT_PLAN_HEADERS,
    _assign_abc_class,
    _count_status,
    _financial_doh,
    _next_count_due,
    _risk_score,
    build_classification_dataframe,
    build_cycle_count_plan_dataframe,
    compute_dashboard_classification_kpis,
    compute_turnover_summary,
    validate_abc_thresholds,
)


def test_validate_abc_thresholds_accepts_defaults():
    """Default thresholds satisfy 0 < A < B < 1."""
    validate_abc_thresholds()


def test_validate_abc_thresholds_rejects_invalid():
    """Invalid threshold combinations raise ValueError."""
    with pytest.raises(ValueError):
        validate_abc_thresholds(a_threshold=0.95, b_threshold=0.80)


def test_assign_abc_class_boundaries():
    """Cumulative pct at A and B thresholds map inclusively."""
    assert _assign_abc_class(ABC_A_THRESHOLD) == "A"
    assert _assign_abc_class(ABC_A_THRESHOLD + 0.0001) == "B"
    assert _assign_abc_class(ABC_B_THRESHOLD) == "B"
    assert _assign_abc_class(ABC_B_THRESHOLD + 0.0001) == "C"


def test_abc_ranking_and_cumulative_values():
    """ABC table ranks by usage value and cumulative pct ends at 1."""
    data = generate_all_data()
    df = build_classification_dataframe(data)
    assert list(df.columns) == CLASSIFICATION_HEADERS
    assert not df.empty
    assert df["Value Rank"].is_monotonic_increasing
    assert df.iloc[-1]["Cumulative Usage %"] == pytest.approx(1.0, abs=0.001)
    assert set(df["ABC Class"].unique()).issubset({"A", "B", "C"})


def test_abc_class_coverage():
    """Every enterprise SKU receives an ABC class."""
    data = generate_all_data()
    classification = build_classification_dataframe(data)
    inventory = data["inventory_full"]
    assert classification["SKU"].nunique() >= inventory["sku"].nunique()


def test_turnover_never_nan_or_infinity():
    """Turnover at all aggregation levels stays finite."""
    data = generate_all_data()
    turnover = compute_turnover_summary(data)
    assert turnover
    for value in turnover.values():
        assert math.isfinite(value)
        assert value >= 0


def test_turnover_zero_inventory_case():
    """Zero average inventory yields turnover of 0, not infinity."""
    data = generate_all_data()
    classification = build_classification_dataframe(data)
    zero_turnover = classification[classification["Average Inventory Value"] == 0]
    if not zero_turnover.empty:
        assert (zero_turnover["Inventory Turnover"] == 0).all()


def test_financial_doh_no_demand_status():
    """Zero turnover uses No Demand status instead of infinity."""
    doh, status = _financial_doh(0.0)
    assert doh is None
    assert status == "No Demand"


def test_unit_accuracy_bounds():
    """Unit accuracy percentages stay within [0, 1]."""
    data = generate_all_data()
    classification = build_classification_dataframe(data)
    assert (classification["Unit Accuracy %"] >= 0).all()
    assert (classification["Unit Accuracy %"] <= 1).all()
    assert (classification["Exact Match Rate"] >= 0).all()
    assert (classification["Exact Match Rate"] <= 1).all()


def test_count_status_date_logic():
    """Count status reflects days until due relative to AS_OF_DATE."""
    overdue_due = AS_OF_DATE - timedelta(days=1)
    assert _count_status(overdue_due, None) == "Overdue"
    assert _count_status(AS_OF_DATE, None) == "Due"
    assert _count_status(AS_OF_DATE + timedelta(days=3), None) == "Due Soon"
    assert _count_status(AS_OF_DATE + timedelta(days=30), None) == "Scheduled"
    assert _count_status(AS_OF_DATE, "Recount Required") == "Recount Required"


def test_next_count_due_frequency():
    """ABC class drives monthly, quarterly, or semiannual intervals."""
    base = date(2026, 1, 1)
    assert _next_count_due(base, "A") == base + timedelta(days=30)
    assert _next_count_due(base, "B") == base + timedelta(days=91)
    assert _next_count_due(base, "C") == base + timedelta(days=182)


def test_risk_score_range():
    """Risk scores stay within documented 0-100 range."""
    for abc in ("A", "B", "C"):
        for status in ("Scheduled", "Due Soon", "Due", "Overdue"):
            score = _risk_score(abc, 50.0, 5, 100, True, status)
            assert 0 <= score <= 100


def test_cycle_count_plan_sorting():
    """Plan sorts overdue first, then by descending risk score."""
    data = generate_all_data()
    plan = build_cycle_count_plan_dataframe(data)
    assert list(plan.columns) == CYCLE_COUNT_PLAN_HEADERS
    assert not plan.empty
    overdue_mask = plan["Count Status"] == "Overdue"
    if overdue_mask.any():
        first_non_overdue = plan[~overdue_mask].index.min()
        assert plan.index[overdue_mask].max() < first_non_overdue
    assert plan["Risk Score"].between(0, 100).all()
    assert plan["Count Priority"].is_monotonic_increasing


def test_dashboard_classification_kpis():
    """Dashboard KPI helper returns expected keys and finite values."""
    data = generate_all_data()
    kpis = compute_dashboard_classification_kpis(data)
    assert kpis["abc_a_count"] + kpis["abc_b_count"] + kpis["abc_c_count"] > 0
    assert math.isfinite(kpis["enterprise_turnover"])
    assert 0 <= kpis["avg_unit_accuracy_pct"] <= 1
    assert kpis["overdue_count"] >= 0
