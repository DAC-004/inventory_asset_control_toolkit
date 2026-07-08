"""Pydantic models for recommendations and KPIs."""

from pydantic import BaseModel, Field


class TransferRecommendation(BaseModel):
    sku: str
    product_name: str
    source_location: str
    destination_location: str
    source_excess_qty: float
    destination_need_qty: float
    suggested_transfer_qty: float
    transfer_cost_per_unit: float
    total_transfer_cost: float
    estimated_margin_protected: float
    net_benefit: float
    recommendation: str
    confidence_level: str
    explanation: str


class MarkdownRecommendation(BaseModel):
    sku: str
    product_name: str
    location: str
    inventory_age_days: int
    current_retail_price: float
    unit_cost: float
    current_margin: float
    suggested_markdown_pct: float
    markdown_price: float
    projected_sell_through_pct: float
    estimated_recovery_value: float
    margin_impact: float
    recommended_disposition: str
    explanation: str


class DashboardKPIs(BaseModel):
    total_inventory_value: float
    aged_inventory_value: float
    excess_inventory_value: float
    slow_moving_sku_count: int
    obsolete_sku_count: int
    transfer_candidate_count: int
    markdown_candidate_count: int
    stockout_risk_count: int
    estimated_recovery_value: float
    average_gross_margin_percent: float
    inventory_turnover: float
    gmroi: float
    average_days_of_supply: float
    exception_count: int = 0
    total_sku_locations: int = 0


class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
