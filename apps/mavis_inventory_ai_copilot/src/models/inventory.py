"""Pydantic models for inventory records."""

from pydantic import BaseModel, Field


class InventoryRecord(BaseModel):
    sku: str
    product_name: str
    category: str
    location: str
    location_type: str
    region: str
    on_hand_qty: float = Field(ge=0)
    min_stock: float = Field(ge=0)
    max_stock: float = Field(ge=0)
    unit_cost: float = Field(ge=0)
    retail_price: float = Field(ge=0)
    inventory_age_days: int = Field(ge=0)
    demand_90_day: float = Field(ge=0)
    avg_weekly_sales: float = Field(ge=0)
    discontinued_flag: bool
    transfer_cost_per_unit: float = Field(ge=0)


class InventoryHealthRecord(InventoryRecord):
    inventory_value: float
    gross_margin: float
    gross_margin_percent: float
    excess_qty: float
    days_of_supply: float
    sell_through_rate: float
    aged_flag: bool
    excess_flag: bool
    slow_moving_flag: bool
    obsolete_flag: bool
    stockout_risk_flag: bool
    issue_type: str
    risk_level: str
    recommended_action: str
    recommendation_reason: str
