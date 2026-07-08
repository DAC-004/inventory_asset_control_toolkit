"""Dashboard KPI aggregation service."""

from __future__ import annotations

import numpy as np

from src.models.inventory import InventoryHealthRecord
from src.models.recommendations import DashboardKPIs, MarkdownRecommendation, TransferRecommendation
from src.services import kpi_service
from src.services.inventory_health_service import get_exception_records


def calculate_dashboard_kpis(
    records: list[InventoryHealthRecord],
    transfers: list[TransferRecommendation] | None = None,
    markdowns: list[MarkdownRecommendation] | None = None,
) -> DashboardKPIs:
    """Aggregate portfolio-level KPIs from classified inventory records."""
    transfers = transfers or []
    markdowns = markdowns or []

    total_value = sum(r.inventory_value for r in records)
    aged_value = sum(r.inventory_value for r in records if r.aged_flag)
    excess_value = sum(r.excess_qty * r.unit_cost for r in records if r.excess_flag)

    slow_skus = {r.sku for r in records if r.slow_moving_flag}
    obsolete_skus = {r.sku for r in records if r.obsolete_flag}
    stockout_count = sum(1 for r in records if r.stockout_risk_flag)

    transfer_candidates = [
        t for t in transfers if t.recommendation == "Transfer Recommended"
    ]
    recovery = sum(m.estimated_recovery_value for m in markdowns)

    gm_pcts = [r.gross_margin_percent for r in records if r.retail_price > 0]
    turnovers = [kpi_service.inventory_turnover(r.demand_90_day, r.unit_cost, r.inventory_value) for r in records if r.inventory_value > 0]
    gmrois = [kpi_service.gmroi(r.demand_90_day, r.gross_margin, r.inventory_value) for r in records if r.inventory_value > 0]

    exceptions = get_exception_records(records)

    return DashboardKPIs(
        total_inventory_value=total_value,
        aged_inventory_value=aged_value,
        excess_inventory_value=excess_value,
        slow_moving_sku_count=len(slow_skus),
        obsolete_sku_count=len(obsolete_skus),
        transfer_candidate_count=len(transfer_candidates),
        markdown_candidate_count=len(markdowns),
        stockout_risk_count=stockout_count,
        estimated_recovery_value=recovery,
        average_gross_margin_percent=float(np.mean(gm_pcts)) if gm_pcts else 0.0,
        inventory_turnover=float(np.mean(turnovers)) if turnovers else 0.0,
        gmroi=float(np.mean(gmrois)) if gmrois else 0.0,
        average_days_of_supply=kpi_service.average_days_of_supply(records),
        exception_count=len(exceptions),
        total_sku_locations=len(records),
    )
