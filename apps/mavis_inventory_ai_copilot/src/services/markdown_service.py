"""Markdown recommendation engine."""

from __future__ import annotations

from src.models.inventory import InventoryHealthRecord
from src.models.recommendations import MarkdownRecommendation, TransferRecommendation
from src.utils.formatting import format_currency


def suggested_markdown_pct(
    obsolete_flag: bool,
    inventory_age_days: int,
    sell_through_rate: float,
) -> float:
    if obsolete_flag or inventory_age_days >= 365:
        return 0.40
    if inventory_age_days >= 240 and sell_through_rate < 0.10:
        return 0.30
    if inventory_age_days >= 180 and sell_through_rate < 0.25:
        return 0.20
    return 0.10


def markdown_price(retail_price: float, markdown_pct: float) -> float:
    return retail_price * (1 - markdown_pct)


def projected_sell_through_pct(markdown_pct: float) -> float:
    if markdown_pct >= 0.40:
        return 0.75
    if markdown_pct >= 0.30:
        return 0.60
    if markdown_pct >= 0.20:
        return 0.45
    return 0.30


def estimated_recovery_value(
    on_hand_qty: float, markdown_price_value: float, projected_pct: float
) -> float:
    return on_hand_qty * markdown_price_value * projected_pct


def margin_impact(on_hand_qty: float, retail_price: float, markdown_price_value: float) -> float:
    return on_hand_qty * (retail_price - markdown_price_value)


def recommended_disposition(
    obsolete_flag: bool,
    demand_90_day: float,
    markdown_pct: float,
) -> str:
    if obsolete_flag and demand_90_day == 0:
        return "Liquidate"
    if markdown_pct >= 0.30:
        return "Aggressive Markdown"
    if markdown_pct >= 0.20:
        return "Controlled Markdown"
    return "Monitor / Light Markdown"


def _is_markdown_candidate(record: InventoryHealthRecord) -> bool:
    return record.issue_type in {
        "Obsolete",
        "Excess/Aged",
        "Excess",
        "Slow-Moving",
        "Aged",
    }


def generate_markdown_recommendations(
    records: list[InventoryHealthRecord],
    transfers: list[TransferRecommendation] | None = None,
) -> list[MarkdownRecommendation]:
    """Generate markdown recommendations for exception inventory."""
    transfer_pairs = set()
    if transfers:
        transfer_pairs = {
            (t.sku, t.source_location) for t in transfers if t.recommendation == "Transfer Recommended"
        }

    recommendations: list[MarkdownRecommendation] = []

    for record in records:
        if not _is_markdown_candidate(record):
            continue
        if (record.sku, record.location) in transfer_pairs:
            continue

        md_pct = suggested_markdown_pct(
            record.obsolete_flag, record.inventory_age_days, record.sell_through_rate
        )
        md_price = markdown_price(record.retail_price, md_pct)
        projected = projected_sell_through_pct(md_pct)
        recovery = estimated_recovery_value(record.on_hand_qty, md_price, projected)
        impact = margin_impact(record.on_hand_qty, record.retail_price, md_price)
        disposition = recommended_disposition(
            record.obsolete_flag, record.demand_90_day, md_pct
        )

        explanation = (
            f"{record.sku} at {record.location}: {md_pct:.0%} markdown to "
            f"{format_currency(md_price, 2)} based on age ({record.inventory_age_days} days) "
            f"and sell-through ({record.sell_through_rate:.1%}). "
            f"Estimated recovery {format_currency(recovery)}."
        )

        recommendations.append(
            MarkdownRecommendation(
                sku=record.sku,
                product_name=record.product_name,
                location=record.location,
                inventory_age_days=record.inventory_age_days,
                current_retail_price=record.retail_price,
                unit_cost=record.unit_cost,
                current_margin=record.gross_margin,
                suggested_markdown_pct=md_pct,
                markdown_price=md_price,
                projected_sell_through_pct=projected,
                estimated_recovery_value=recovery,
                margin_impact=impact,
                recommended_disposition=disposition,
                explanation=explanation,
            )
        )

    recommendations.sort(key=lambda r: r.estimated_recovery_value, reverse=True)
    return recommendations
