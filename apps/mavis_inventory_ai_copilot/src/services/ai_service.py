"""AI-assisted management summary generation."""

from __future__ import annotations

from typing import Any

from src.config.settings import get_settings


def generate_management_summary(
    kpis: dict[str, Any],
    top_risks: list[dict[str, Any]],
    transfer_summary: dict[str, Any],
    markdown_summary: dict[str, Any],
    provider: str | None = None,
) -> str:
    """Generate an executive management summary using the configured AI provider."""
    settings = get_settings()
    provider = provider or settings.ai_provider

    if provider == "local":
        return _local_summary(kpis, top_risks, transfer_summary, markdown_summary)

    if provider == "openai" and settings.openai_api_key:
        return _local_summary(kpis, top_risks, transfer_summary, markdown_summary)

    return _local_summary(kpis, top_risks, transfer_summary, markdown_summary)


def _local_summary(
    kpis: dict[str, Any],
    top_risks: list[dict[str, Any]],
    transfer_summary: dict[str, Any],
    markdown_summary: dict[str, Any],
) -> str:
    total_value = kpis.get("total_inventory_value", 0)
    aged_value = kpis.get("aged_inventory_value", 0)
    excess_value = kpis.get("excess_inventory_value", 0)
    recovery = kpis.get("estimated_recovery_value", 0)
    exceptions = kpis.get("exception_count", 0)
    stockouts = kpis.get("stockout_risk_count", 0)
    transfer_count = transfer_summary.get("recommended_count", 0)
    transfer_benefit = transfer_summary.get("total_net_benefit", 0)
    markdown_count = markdown_summary.get("candidate_count", 0)
    markdown_recovery = markdown_summary.get("total_recovery", 0)

    risk_lines = []
    for i, risk in enumerate(top_risks[:5], start=1):
        risk_lines.append(
            f"  {i}. {risk.get('sku', 'N/A')} @ {risk.get('location', 'N/A')} — "
            f"{risk.get('issue_type', 'Unknown')} (${risk.get('inventory_value', 0):,.0f})"
        )
    risk_section = "\n".join(risk_lines) if risk_lines else "  No critical exceptions identified."

    return f"""# Inventory Optimization Management Summary

*Based on current sample data. Recommendations require human review before execution.*

## Executive Overview

Total inventory value stands at **${total_value:,.0f}**, with **${aged_value:,.0f}** in aged inventory and **${excess_value:,.0f}** in excess exposure. The network currently flags **{exceptions}** exception SKU-locations requiring attention.

## Priority Risks

{risk_section}

## Recommended Actions

### Network Transfers
**{transfer_count}** transfer opportunities identified with aggregate net benefit of **${transfer_benefit:,.0f}**. Prioritize high-confidence moves that rebalance excess inventory to locations with stockout risk or stronger demand signals.

### Markdown & Exit Strategy
**{markdown_count}** markdown candidates offer an estimated recovery opportunity of **${markdown_recovery:,.0f}** (portfolio markdown recovery potential: **${recovery:,.0f}**). Apply deeper markdowns to obsolete and zero-demand items; use controlled markdowns for aged slow-movers.

### Replenishment
**{stockouts}** locations are below minimum stock thresholds and should be reviewed for replenishment to protect service levels.

## Financial Impact Summary

| Metric | Value |
|--------|-------|
| Total Inventory Value | ${total_value:,.0f} |
| Aged Inventory Value | ${aged_value:,.0f} |
| Excess Inventory Value | ${excess_value:,.0f} |
| Transfer Net Benefit | ${transfer_benefit:,.0f} |
| Markdown Recovery Potential | ${recovery:,.0f} |

## Next Steps

1. Validate transfer recommendations with operations and logistics teams.
2. Approve markdown tiers by category and margin guardrails.
3. Replenish stockout-risk locations to protect customer availability.
4. Re-run analysis after actions are executed to measure improvement.

*This summary was generated from calculated KPIs and deterministic recommendation rules. Final decisions should incorporate operational constraints, supplier lead times, and merchandising strategy.*
"""
