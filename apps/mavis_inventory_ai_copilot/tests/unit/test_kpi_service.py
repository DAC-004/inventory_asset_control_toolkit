"""Unit tests for KPI calculations."""

from src.services import kpi_service


def test_inventory_value_calculation():
    assert kpi_service.inventory_value(10, 25.0) == 250.0


def test_gross_margin_calculation():
    assert kpi_service.gross_margin(150.0, 100.0) == 50.0


def test_gross_margin_percent_handles_zero_price():
    assert kpi_service.gross_margin_percent(0, 100.0) == 0.0


def test_days_of_supply_normal_case():
    assert kpi_service.days_of_supply(70, 10.0) == 49.0


def test_days_of_supply_zero_sales_returns_999():
    assert kpi_service.days_of_supply(100, 0) == 999


def test_sell_through_rate_normal_case():
    assert kpi_service.sell_through_rate(30, 70) == 0.3


def test_sell_through_rate_zero_denominator():
    assert kpi_service.sell_through_rate(0, 0) == 0.0


def test_gmroi_calculation():
    assert kpi_service.gmroi(20, 50.0, 1000.0) == 1.0


def test_gmroi_zero_inventory_value():
    assert kpi_service.gmroi(20, 50.0, 0) == 0.0
