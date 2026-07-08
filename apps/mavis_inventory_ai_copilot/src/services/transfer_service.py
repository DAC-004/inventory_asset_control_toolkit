"""Transfer recommendation engine."""

from __future__ import annotations

from src.config.constants import (
    HIGH_NET_BENEFIT_THRESHOLD,
    MEDIUM_NET_BENEFIT_THRESHOLD,
    STOCKOUT_DOS_THRESHOLD,
)
from src.models.inventory import InventoryHealthRecord
from src.models.recommendations import TransferRecommendation


def is_source_eligible(record: InventoryHealthRecord) -> bool:
    return record.on_hand_qty > record.max_stock and record.excess_qty > 0


def is_destination_eligible(record: InventoryHealthRecord) -> bool:
    return (
        record.on_hand_qty < record.min_stock
        or record.days_of_supply < STOCKOUT_DOS_THRESHOLD
    )


def destination_need_qty(record: InventoryHealthRecord) -> float:
    need = max(record.min_stock - record.on_hand_qty, 0)
    if need == 0 and record.avg_weekly_sales > 0:
        need = max(record.avg_weekly_sales * 4 - record.on_hand_qty, 0)
    return need


def suggested_transfer_qty(source: InventoryHealthRecord, dest: InventoryHealthRecord) -> float:
    need = destination_need_qty(dest)
    return min(source.excess_qty, need)


def total_transfer_cost(qty: float, cost_per_unit: float) -> float:
    return qty * cost_per_unit


def estimated_margin_protected(qty: float, gross_margin: float) -> float:
    return qty * gross_margin


def net_benefit(margin_protected: float, transfer_cost: float) -> float:
    return margin_protected - transfer_cost


def confidence_level(benefit: float) -> str:
    if benefit >= HIGH_NET_BENEFIT_THRESHOLD:
        return "High"
    if benefit >= MEDIUM_NET_BENEFIT_THRESHOLD:
        return "Medium"
    return "Low"


def generate_transfer_recommendations(
    records: list[InventoryHealthRecord],
) -> list[TransferRecommendation]:
    """Generate ranked transfer recommendations across the network."""
    by_network: dict[str, list[InventoryHealthRecord]] = {}
    for record in records:
        network_key = record.product_name.strip().lower()
        by_network.setdefault(network_key, []).append(record)

    recommendations: list[TransferRecommendation] = []

    for network_key, network_records in by_network.items():
        if len(network_records) < 2:
            continue

        sources = [r for r in network_records if is_source_eligible(r)]
        destinations = [r for r in network_records if is_destination_eligible(r)]

        for source in sources:
            for dest in destinations:
                if source.location == dest.location:
                    continue

                qty = suggested_transfer_qty(source, dest)
                if qty <= 0:
                    continue

                cost_per_unit = source.transfer_cost_per_unit
                total_cost = total_transfer_cost(qty, cost_per_unit)
                margin_protected = estimated_margin_protected(qty, source.gross_margin)
                benefit = net_benefit(margin_protected, total_cost)

                if benefit <= 0:
                    continue

                need = destination_need_qty(dest)
                rec_label = "Transfer Recommended"
                explanation = (
                    f"Move {qty:.0f} units of {source.product_name} ({source.sku}) "
                    f"from {source.location} (excess {source.excess_qty:.0f}) to "
                    f"{dest.location} (need {need:.0f}). Net benefit ${benefit:,.0f} "
                    f"after ${total_cost:,.0f} transfer cost."
                )

                recommendations.append(
                    TransferRecommendation(
                        sku=source.sku,
                        product_name=source.product_name,
                        source_location=source.location,
                        destination_location=dest.location,
                        source_excess_qty=source.excess_qty,
                        destination_need_qty=need,
                        suggested_transfer_qty=qty,
                        transfer_cost_per_unit=cost_per_unit,
                        total_transfer_cost=total_cost,
                        estimated_margin_protected=margin_protected,
                        net_benefit=benefit,
                        recommendation=rec_label,
                        confidence_level=confidence_level(benefit),
                        explanation=explanation,
                    )
                )

    recommendations.sort(key=lambda r: r.net_benefit, reverse=True)
    return recommendations
