"""Unit tests for management summary generation."""

from src.services.ai_service import generate_management_summary


def test_local_summary_generates_text():
    text = generate_management_summary({}, [], {}, {}, provider="local")
    assert isinstance(text, str)
    assert len(text) > 100


def test_summary_includes_total_inventory_value():
    kpis = {"total_inventory_value": 123456.0}
    text = generate_management_summary(kpis, [], {}, {}, provider="local")
    assert "123,456" in text


def test_summary_includes_top_risk_count():
    risks = [{"sku": "A", "location": "L", "issue_type": "Excess", "inventory_value": 5000}]
    text = generate_management_summary({}, risks, {}, {}, provider="local")
    assert "A @ L" in text


def test_summary_does_not_fail_with_empty_recommendations():
    text = generate_management_summary(
        {"total_inventory_value": 0, "exception_count": 0},
        [],
        {"recommended_count": 0, "total_net_benefit": 0},
        {"candidate_count": 0, "total_recovery": 0},
        provider="local",
    )
    assert "human review" in text.lower()
