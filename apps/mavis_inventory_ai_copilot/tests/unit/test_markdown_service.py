"""Unit tests for markdown recommendations."""

from src.models.inventory import InventoryRecord
from src.services.inventory_health_service import classify_inventory
from src.services import markdown_service


def _health(**overrides):
    base = dict(
        sku="MD-100",
        product_name="Item",
        category="Cat",
        location="Store-A",
        location_type="Store",
        region="East",
        on_hand_qty=50,
        min_stock=10,
        max_stock=30,
        unit_cost=20.0,
        retail_price=40.0,
        inventory_age_days=200,
        demand_90_day=2,
        avg_weekly_sales=1.0,
        discontinued_flag=False,
        transfer_cost_per_unit=2.5,
    )
    base.update(overrides)
    return classify_inventory([InventoryRecord(**base)])[0]


def test_obsolete_item_gets_40_percent_markdown():
    record = _health(discontinued_flag=True, inventory_age_days=400, demand_90_day=0)
    pct = markdown_service.suggested_markdown_pct(
        record.obsolete_flag, record.inventory_age_days, record.sell_through_rate
    )
    assert pct == 0.40


def test_aged_low_sellthrough_item_gets_30_percent_markdown():
    record = _health(inventory_age_days=250, demand_90_day=1, avg_weekly_sales=0.5)
    pct = markdown_service.suggested_markdown_pct(
        record.obsolete_flag, record.inventory_age_days, record.sell_through_rate
    )
    assert pct == 0.30


def test_moderate_aged_item_gets_20_percent_markdown():
    record = _health(inventory_age_days=190, demand_90_day=5, avg_weekly_sales=2.0)
    pct = markdown_service.suggested_markdown_pct(
        record.obsolete_flag, record.inventory_age_days, record.sell_through_rate
    )
    assert pct == 0.20


def test_light_markdown_default():
    record = _health(inventory_age_days=90, demand_90_day=20, avg_weekly_sales=5.0, on_hand_qty=25)
    pct = markdown_service.suggested_markdown_pct(
        record.obsolete_flag, record.inventory_age_days, record.sell_through_rate
    )
    assert pct == 0.10


def test_markdown_price():
    assert markdown_service.markdown_price(100.0, 0.20) == 80.0


def test_estimated_recovery_value():
    assert markdown_service.estimated_recovery_value(10, 80.0, 0.45) == 360.0


def test_liquidation_disposition_for_obsolete_zero_demand():
    record = _health(discontinued_flag=True, inventory_age_days=400, demand_90_day=0)
    disp = markdown_service.recommended_disposition(
        record.obsolete_flag, record.demand_90_day, 0.40
    )
    assert disp == "Liquidate"
