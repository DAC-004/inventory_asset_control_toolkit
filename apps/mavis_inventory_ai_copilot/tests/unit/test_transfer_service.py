"""Unit tests for transfer recommendations."""

from src.models.inventory import InventoryRecord
from src.services.inventory_health_service import classify_inventory
from src.services import transfer_service


def _pair_records():
    source = InventoryRecord(
        sku="TR-100",
        product_name="Tire",
        category="Tires",
        location="DC-A",
        location_type="DC",
        region="East",
        on_hand_qty=100,
        min_stock=10,
        max_stock=40,
        unit_cost=80.0,
        retail_price=120.0,
        inventory_age_days=200,
        demand_90_day=5,
        avg_weekly_sales=2.0,
        discontinued_flag=False,
        transfer_cost_per_unit=2.5,
    )
    dest = InventoryRecord(
        sku="TR-100",
        product_name="Tire",
        category="Tires",
        location="Store-B",
        location_type="Store",
        region="East",
        on_hand_qty=5,
        min_stock=20,
        max_stock=50,
        unit_cost=80.0,
        retail_price=120.0,
        inventory_age_days=30,
        demand_90_day=30,
        avg_weekly_sales=10.0,
        discontinued_flag=False,
        transfer_cost_per_unit=2.5,
    )
    return classify_inventory([source, dest])


def test_source_eligibility_with_excess_qty():
    records = _pair_records()
    assert transfer_service.is_source_eligible(records[0]) is True


def test_destination_eligibility_with_low_stock():
    records = _pair_records()
    assert transfer_service.is_destination_eligible(records[1]) is True


def test_suggested_transfer_qty_uses_min_of_source_and_need():
    records = _pair_records()
    qty = transfer_service.suggested_transfer_qty(records[0], records[1])
    need = transfer_service.destination_need_qty(records[1])
    assert qty == min(records[0].excess_qty, need)
    assert qty > 0


def test_total_transfer_cost():
    assert transfer_service.total_transfer_cost(10, 2.5) == 25.0


def test_estimated_margin_protected():
    assert transfer_service.estimated_margin_protected(10, 40.0) == 400.0


def test_net_benefit():
    assert transfer_service.net_benefit(400.0, 25.0) == 375.0


def test_transfer_recommended_when_net_benefit_positive(sample_health_records):
    recs = transfer_service.generate_transfer_recommendations(sample_health_records)
    assert any(r.recommendation == "Transfer Recommended" for r in recs)


def test_no_transfer_when_cost_exceeds_benefit():
    source = InventoryRecord(
        sku="LOW",
        product_name="Low Margin",
        category="Cat",
        location="DC-1",
        location_type="DC",
        region="East",
        on_hand_qty=42,
        min_stock=5,
        max_stock=40,
        unit_cost=100.0,
        retail_price=100.5,
        inventory_age_days=200,
        demand_90_day=1,
        avg_weekly_sales=1.0,
        discontinued_flag=False,
        transfer_cost_per_unit=50.0,
    )
    dest = InventoryRecord(
        sku="LOW",
        product_name="Low Margin",
        category="Cat",
        location="Store-1",
        location_type="Store",
        region="East",
        on_hand_qty=1,
        min_stock=10,
        max_stock=40,
        unit_cost=100.0,
        retail_price=100.5,
        inventory_age_days=30,
        demand_90_day=5,
        avg_weekly_sales=2.0,
        discontinued_flag=False,
        transfer_cost_per_unit=50.0,
    )
    records = classify_inventory([source, dest])
    recs = transfer_service.generate_transfer_recommendations(records)
    assert len(recs) == 0
