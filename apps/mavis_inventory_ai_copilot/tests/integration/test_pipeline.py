"""End-to-end pipeline integration tests."""

from src.data.sample_data import load_sample_inventory
from src.data.transformers import enrich_discontinued_flag, to_inventory_records
from src.services.ai_service import generate_management_summary
from src.services.inventory_health_service import classify_inventory
from src.services.kpi_dashboard_service import calculate_dashboard_kpis
from src.services.markdown_service import generate_markdown_recommendations
from src.services.summary_service import run_pipeline
from src.services.transfer_service import generate_transfer_recommendations


def test_sample_data_loads(sample_csv_path):
    df = load_sample_inventory()
    assert len(df) > 0


def test_pipeline_generates_health_records(normalized_sample_df):
    records = to_inventory_records(enrich_discontinued_flag(normalized_sample_df))
    health = classify_inventory(records)
    assert len(health) == len(records)
    assert any(h.issue_type != "Healthy" for h in health)


def test_pipeline_generates_kpis(normalized_sample_df):
    records = classify_inventory(to_inventory_records(enrich_discontinued_flag(normalized_sample_df)))
    transfers = generate_transfer_recommendations(records)
    markdowns = generate_markdown_recommendations(records, transfers)
    kpis = calculate_dashboard_kpis(records, transfers, markdowns)
    assert kpis.total_inventory_value > 0


def test_pipeline_generates_transfer_recommendations(normalized_sample_df):
    records = classify_inventory(to_inventory_records(enrich_discontinued_flag(normalized_sample_df)))
    transfers = generate_transfer_recommendations(records)
    assert isinstance(transfers, list)


def test_pipeline_generates_markdown_recommendations(normalized_sample_df):
    records = classify_inventory(to_inventory_records(enrich_discontinued_flag(normalized_sample_df)))
    markdowns = generate_markdown_recommendations(records)
    assert len(markdowns) > 0


def test_pipeline_generates_management_summary(sample_csv_path):
    result = run_pipeline(sample_csv_path)
    assert result.management_summary
    assert result.kpis.total_inventory_value > 0
    summary = generate_management_summary(
        result.kpis.model_dump(),
        [],
        {"recommended_count": 0, "total_net_benefit": 0},
        {"candidate_count": 0, "total_recovery": 0},
        provider="local",
    )
    assert "Management Summary" in summary
