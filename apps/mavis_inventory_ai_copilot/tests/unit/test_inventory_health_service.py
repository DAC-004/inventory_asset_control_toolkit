"""Unit tests for inventory health classification."""

from src.models.inventory import InventoryRecord
from src.services.inventory_health_service import classify_inventory


def _record(**overrides) -> InventoryRecord:
    base = dict(
        sku="X-001",
        product_name="Test",
        category="Cat",
        location="Loc",
        location_type="Retail",
        region="East",
        on_hand_qty=20,
        min_stock=10,
        max_stock=30,
        unit_cost=10.0,
        retail_price=20.0,
        inventory_age_days=30,
        demand_90_day=15,
        avg_weekly_sales=5.0,
        discontinued_flag=False,
        transfer_cost_per_unit=2.5,
    )
    base.update(overrides)
    return InventoryRecord(**base)


def test_excess_flag_when_on_hand_exceeds_max_stock():
    result = classify_inventory([_record(on_hand_qty=50, max_stock=30)])[0]
    assert result.excess_flag is True


def test_aged_flag_at_180_days():
    result = classify_inventory([_record(inventory_age_days=180)])[0]
    assert result.aged_flag is True


def test_slow_moving_flag():
    result = classify_inventory([
        _record(on_hand_qty=200, avg_weekly_sales=1.0, demand_90_day=5, inventory_age_days=60)
    ])[0]
    assert result.slow_moving_flag is True


def test_obsolete_flag_for_discontinued_item():
    result = classify_inventory([_record(discontinued_flag=True)])[0]
    assert result.obsolete_flag is True
    assert result.issue_type == "Obsolete"


def test_stockout_risk_when_below_min_stock():
    result = classify_inventory([_record(on_hand_qty=5, min_stock=10)])[0]
    assert result.stockout_risk_flag is True


def test_issue_type_priority_obsolete_before_excess():
    result = classify_inventory([
        _record(discontinued_flag=True, on_hand_qty=50, max_stock=30)
    ])[0]
    assert result.issue_type == "Obsolete"


def test_risk_level_high_for_high_value_excess_aged():
    result = classify_inventory([
        _record(
            on_hand_qty=200,
            max_stock=30,
            unit_cost=100.0,
            inventory_age_days=200,
        )
    ])[0]
    assert result.issue_type == "Excess/Aged"
    assert result.risk_level == "High"


def test_recommended_action_replenish_for_stockout():
    result = classify_inventory([_record(on_hand_qty=3, min_stock=10)])[0]
    assert result.recommended_action == "Replenish"
