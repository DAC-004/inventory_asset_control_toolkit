"""Vendor scorecards — OTIF, quality, lead time, price, and weighted scoring."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

from config.workbook_config import (
    MIN_VENDOR_PO_SAMPLES,
    VENDOR_RISK_APPROVED_MIN,
    VENDOR_RISK_PREFERRED_MIN,
    VENDOR_RISK_WATCH_MIN,
    VENDOR_SCORE_WEIGHTS,
)
from src.services.purchase_order_service import build_po_tracker_dataframe

VENDOR_SCORECARD_HEADERS = [
    "Supplier ID",
    "Supplier Name",
    "Supplier Category",
    "PO Line Count",
    "Delivery Count",
    "Open PO Value",
    "On-Time Delivery %",
    "In-Full Delivery %",
    "OTIF %",
    "Quality Acceptance %",
    "Average Lead Time (Days)",
    "Lead-Time Variability",
    "Average Days Late",
    "Late Delivery Rate",
    "Purchase Price Variance %",
    "Responsiveness Score",
    "Administrative Compliance Score",
    "OTIF Component Score",
    "Quality Component Score",
    "Lead-Time Consistency Score",
    "Price Performance Score",
    "Responsiveness Component Score",
    "Compliance Component Score",
    "Total Vendor Score",
    "Risk Class",
    "Primary Gap",
    "Recommended Action",
]


def validate_vendor_score_weights(
    weights: dict[str, float] | None = None,
) -> None:
    """Ensure vendor score weights sum to 100%."""
    weights = weights or VENDOR_SCORE_WEIGHTS
    total = sum(weights.values())
    if not math.isclose(total, 1.0, abs_tol=0.001):
        raise ValueError(f"Vendor score weights must sum to 1.0; got {total}")


def _finite_rate(value: float) -> float:
    if not math.isfinite(value):
        return 0.0
    return max(0.0, min(1.0, value))


def _safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0 or not math.isfinite(denominator):
        return 0.0
    return _finite_rate(numerator / denominator)


def _rating_to_score(rating: float) -> float:
    """Normalize 1-5 supplier rating to 0-100."""
    return max(0.0, min(100.0, _safe_div(rating, 5.0) * 100))


def _lead_time_consistency_score(avg_lead: float, std_lead: float) -> float:
    if avg_lead <= 0:
        return 50.0
    cv = std_lead / avg_lead
    return max(0.0, min(100.0, 100.0 - cv * 100))


def _price_performance_score(ppv_pct: float) -> float:
    return max(0.0, min(100.0, 100.0 - abs(ppv_pct)))


def _risk_class(score: float, sample_count: int) -> str:
    if sample_count < MIN_VENDOR_PO_SAMPLES:
        return "Data Insufficient"
    if score >= VENDOR_RISK_PREFERRED_MIN:
        return "Preferred"
    if score >= VENDOR_RISK_APPROVED_MIN:
        return "Approved"
    if score >= VENDOR_RISK_WATCH_MIN:
        return "Watch"
    return "High Risk"


def _primary_gap(components: dict[str, float]) -> tuple[str, str]:
    """Identify weakest component and recommendation."""
    labels = {
        "otif": "On-time in-full delivery",
        "quality": "Quality acceptance",
        "lead_time_consistency": "Lead-time consistency",
        "price_performance": "Purchase price performance",
        "responsiveness": "Responsiveness",
        "administrative_compliance": "Administrative compliance",
    }
    actions = {
        "otif": "Improve delivery reliability and fill rates",
        "quality": "Strengthen incoming quality controls with supplier",
        "lead_time_consistency": "Stabilize lead times via SLA review",
        "price_performance": "Renegotiate pricing or benchmark alternatives",
        "responsiveness": "Escalate communication cadence with vendor",
        "administrative_compliance": "Audit PO documentation and compliance process",
    }
    weakest = min(components, key=components.get)  # type: ignore[arg-type]
    return labels[weakest], actions[weakest]


def build_vendor_scorecard_dataframe(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build vendor scorecard rows from PO tracker and supplier master."""
    validate_vendor_score_weights()
    tracker = build_po_tracker_dataframe(data)
    suppliers = data.get("suppliers", pd.DataFrame())

    if suppliers.empty:
        return pd.DataFrame(columns=VENDOR_SCORECARD_HEADERS)

    supplier_meta = suppliers.set_index("supplier_id")

    rows: list[dict[str, Any]] = []
    for supplier_id, meta in supplier_meta.iterrows():
        lines = (
            tracker[tracker["Supplier ID"] == supplier_id]
            if not tracker.empty
            else pd.DataFrame()
        )
        sample_count = len(lines)
        delivered = (
            lines[lines["Final Receipt Date"].notna()]
            if not lines.empty
            else pd.DataFrame()
        )

        on_time = 0
        in_full = 0
        otif = 0
        delivery_count = len(delivered)
        lead_times: list[float] = []
        days_late_list: list[float] = []

        if not delivered.empty:
            for _, row in delivered.iterrows():
                days_late = int(row["Days Late"])
                days_late_list.append(float(days_late))
                on_time_flag = days_late == 0
                in_full_flag = int(row["Accepted Quantity"]) >= int(
                    row["Ordered Quantity"]
                )
                if on_time_flag:
                    on_time += 1
                if in_full_flag:
                    in_full += 1
                if on_time_flag and in_full_flag:
                    otif += 1

                approval = row["Approval Date"]
                final = row["Final Receipt Date"]
                if pd.notna(approval) and pd.notna(final):
                    lead_times.append(
                        float((pd.to_datetime(final) - pd.to_datetime(approval)).days)
                    )

        on_time_pct = _safe_div(on_time, delivery_count)
        in_full_pct = _safe_div(in_full, delivery_count)
        otif_pct = _safe_div(otif, delivery_count)

        received_total = int(lines["Received Quantity"].sum()) if not lines.empty else 0
        accepted_total = int(lines["Accepted Quantity"].sum()) if not lines.empty else 0
        quality_pct = _safe_div(accepted_total, received_total)

        avg_lead = sum(lead_times) / len(lead_times) if lead_times else 0.0
        if len(lead_times) > 1:
            mean_lt = avg_lead
            lead_std = math.sqrt(
                sum((lt - mean_lt) ** 2 for lt in lead_times) / len(lead_times)
            )
        else:
            lead_std = 0.0

        avg_days_late = (
            sum(days_late_list) / len(days_late_list) if days_late_list else 0.0
        )
        late_rate = _safe_div(
            sum(1 for d in days_late_list if d > 0), len(days_late_list)
        )

        ppv_pct = (
            float(lines["Purchase Price Variance %"].mean()) if not lines.empty else 0.0
        )
        open_value = (
            float(lines[lines["Open Quantity"] > 0]["Open PO Value"].sum())
            if not lines.empty
            else 0.0
        )

        responsiveness = _rating_to_score(float(meta.get("responsiveness_rating", 3)))
        compliance = _rating_to_score(
            float(meta.get("administrative_compliance_rating", 3))
        )

        otif_score = otif_pct * 100
        quality_score = quality_pct * 100
        lt_score = _lead_time_consistency_score(avg_lead, lead_std)
        price_score = _price_performance_score(ppv_pct)

        components = {
            "otif": otif_score,
            "quality": quality_score,
            "lead_time_consistency": lt_score,
            "price_performance": price_score,
            "responsiveness": responsiveness,
            "administrative_compliance": compliance,
        }

        total = sum(components[k] * VENDOR_SCORE_WEIGHTS[k] for k in components)
        total = round(max(0.0, min(100.0, total)), 1)
        risk = _risk_class(total, sample_count)
        gap, action = _primary_gap(components)

        rows.append(
            {
                "Supplier ID": supplier_id,
                "Supplier Name": meta["supplier_name"],
                "Supplier Category": meta["supplier_category"],
                "PO Line Count": sample_count,
                "Delivery Count": delivery_count,
                "Open PO Value": round(open_value, 2),
                "On-Time Delivery %": round(on_time_pct, 4),
                "In-Full Delivery %": round(in_full_pct, 4),
                "OTIF %": round(otif_pct, 4),
                "Quality Acceptance %": round(quality_pct, 4),
                "Average Lead Time (Days)": round(avg_lead, 1),
                "Lead-Time Variability": round(lead_std, 2),
                "Average Days Late": round(avg_days_late, 1),
                "Late Delivery Rate": round(late_rate, 4),
                "Purchase Price Variance %": round(ppv_pct, 2),
                "Responsiveness Score": round(responsiveness, 1),
                "Administrative Compliance Score": round(compliance, 1),
                "OTIF Component Score": round(otif_score, 1),
                "Quality Component Score": round(quality_score, 1),
                "Lead-Time Consistency Score": round(lt_score, 1),
                "Price Performance Score": round(price_score, 1),
                "Responsiveness Component Score": round(responsiveness, 1),
                "Compliance Component Score": round(compliance, 1),
                "Total Vendor Score": total,
                "Risk Class": risk,
                "Primary Gap": gap,
                "Recommended Action": action,
            }
        )

    df = pd.DataFrame(rows, columns=VENDOR_SCORECARD_HEADERS)
    if df.empty:
        return df
    return df.sort_values("Total Vendor Score", ascending=False).reset_index(drop=True)


def build_vendor_risk_lookup(data: dict[str, pd.DataFrame]) -> dict[str, str]:
    """Supplier ID to risk class for replenishment integration."""
    scorecards = build_vendor_scorecard_dataframe(data)
    if scorecards.empty:
        return {}
    raw = scorecards.set_index("Supplier ID")["Risk Class"].astype(str)
    return {str(k): str(v) for k, v in raw.items()}


def compute_vendor_scorecard_kpis(df: pd.DataFrame) -> dict[str, Any]:
    """KPI summary for vendor scorecards sheet."""
    if df.empty:
        return {
            "preferred_count": 0,
            "avg_score": 0.0,
            "avg_otif": 0.0,
            "high_risk_count": 0,
        }
    return {
        "preferred_count": int((df["Risk Class"] == "Preferred").sum()),
        "avg_score": round(float(df["Total Vendor Score"].mean()), 1),
        "avg_otif": round(float(df["OTIF %"].mean()), 4),
        "high_risk_count": int((df["Risk Class"] == "High Risk").sum()),
    }
