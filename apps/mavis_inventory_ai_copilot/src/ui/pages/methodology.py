"""Methodology page."""

from __future__ import annotations

import streamlit as st


def render(_pipeline=None) -> None:
    st.markdown("### Methodology")
    st.caption("Business rules, classification logic, and recommendation frameworks.")

    st.markdown(
        """
        #### Inventory Health Classification

        | Flag | Rule |
        |------|------|
        | **Aged** | Inventory age ≥ 180 days |
        | **Excess** | On-hand quantity > max stock |
        | **Slow-Moving** | Days of supply ≥ 120 AND sell-through < 25% AND demand > 0 |
        | **Obsolete** | Discontinued OR age ≥ 365 OR (zero demand AND age ≥ 240) |
        | **Stockout Risk** | On-hand quantity < min stock |

        Issue types follow priority: Obsolete → Excess/Aged → Stockout Risk → Excess →
        Slow-Moving → Aged → Healthy.

        #### KPI Calculations

        - **Inventory Value** = On-hand qty × Unit cost
        - **Days of Supply** = On-hand qty ÷ (Avg weekly sales ÷ 7); capped at 999 when sales = 0
        - **Sell-Through Rate** = 90-day demand ÷ (90-day demand + on-hand qty)
        - **GMROI** = (90-day demand × Gross margin) ÷ Inventory value

        #### Transfer Recommendations

        Sources must have excess above max stock. Destinations must be below min stock or
        have days of supply < 30. Transfer quantity is the minimum of source excess and
        destination need. Recommendations require positive net benefit (margin protected − transfer cost).

        #### Markdown Recommendations

        | Condition | Markdown % |
        |-----------|------------|
        | Obsolete or age ≥ 365 days | 40% |
        | Age ≥ 240 days AND sell-through < 10% | 30% |
        | Age ≥ 180 days AND sell-through < 25% | 20% |
        | Default | 10% |

        Recovery value = On-hand qty × Markdown price × Projected sell-through %.

        #### AI Summary

        The local AI provider uses deterministic templates populated with calculated KPIs.
        No external API keys are required for the demo. External providers are optional
        and receive structured metrics only.

        #### Data Source

        The application ingests the Inventory IT Asset Control Toolkit workbook or CSV export
        without modifying the source file. Column names are normalized to a canonical schema
        for analytics processing.
        """
    )
