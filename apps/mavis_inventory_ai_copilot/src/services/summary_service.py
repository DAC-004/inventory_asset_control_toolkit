"""End-to-end analytics pipeline orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.config.settings import get_settings
from src.data.loaders import load_inventory_data
from src.data.transformers import enrich_discontinued_flag, normalize_columns, to_inventory_records
from src.data.validators import validate_inventory_data
from src.models.inventory import InventoryHealthRecord
from src.models.recommendations import (
    DashboardKPIs,
    MarkdownRecommendation,
    TransferRecommendation,
    ValidationResult,
)
from src.services.ai_service import generate_management_summary
from src.services.inventory_health_service import classify_inventory, get_exception_records
from src.services.kpi_dashboard_service import calculate_dashboard_kpis
from src.services.markdown_service import generate_markdown_recommendations
from src.services.transfer_service import generate_transfer_recommendations


@dataclass
class PipelineResult:
    raw_df: pd.DataFrame
    normalized_df: pd.DataFrame
    validation: ValidationResult
    health_records: list[InventoryHealthRecord]
    kpis: DashboardKPIs
    transfers: list[TransferRecommendation]
    markdowns: list[MarkdownRecommendation]
    management_summary: str
    source_path: Path
    loaded_at: datetime


def run_pipeline(source_path: Path | str | None = None) -> PipelineResult:
    """Load, validate, transform, and analyze inventory data."""
    settings = get_settings()
    path = Path(source_path) if source_path else settings.data_source_path

    raw_df = load_inventory_data(path)
    normalized_df = normalize_columns(raw_df)
    normalized_df = enrich_discontinued_flag(normalized_df)
    validation = validate_inventory_data(normalized_df)

    if not validation.is_valid:
        raise ValueError("; ".join(validation.errors))

    records = to_inventory_records(normalized_df)
    health_records = classify_inventory(records)
    transfers = generate_transfer_recommendations(health_records)
    markdowns = generate_markdown_recommendations(health_records, transfers)
    kpis = calculate_dashboard_kpis(health_records, transfers, markdowns)

    top_risks = _top_risks(health_records)
    transfer_summary = {
        "recommended_count": len([t for t in transfers if t.recommendation == "Transfer Recommended"]),
        "total_net_benefit": sum(t.net_benefit for t in transfers),
    }
    markdown_summary = {
        "candidate_count": len(markdowns),
        "total_recovery": sum(m.estimated_recovery_value for m in markdowns),
    }

    summary = generate_management_summary(
        kpis.model_dump(),
        top_risks,
        transfer_summary,
        markdown_summary,
    )

    return PipelineResult(
        raw_df=raw_df,
        normalized_df=normalized_df,
        validation=validation,
        health_records=health_records,
        kpis=kpis,
        transfers=transfers,
        markdowns=markdowns,
        management_summary=summary,
        source_path=path,
        loaded_at=datetime.now(),
    )


def _top_risks(records: list[InventoryHealthRecord], limit: int = 10) -> list[dict]:
    exceptions = get_exception_records(records)
    sorted_records = sorted(exceptions, key=lambda r: r.inventory_value, reverse=True)
    return [
        {
            "sku": r.sku,
            "location": r.location,
            "issue_type": r.issue_type,
            "inventory_value": r.inventory_value,
            "risk_level": r.risk_level,
        }
        for r in sorted_records[:limit]
    ]
