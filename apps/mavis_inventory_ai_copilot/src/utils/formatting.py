"""Number and display formatting helpers."""

from __future__ import annotations


def format_currency(value: float | int | None, decimals: int = 0) -> str:
    if value is None:
        return "$0"
    return "$" + f"{value:,.{decimals}f}"


def format_percent(value: float | int | None, decimals: int = 1) -> str:
    if value is None:
        return "0.0%"
    return f"{value * 100:.{decimals}f}%"


def format_number(value: float | int | None, decimals: int = 0) -> str:
    if value is None:
        return "0"
    return f"{value:,.{decimals}f}"


def risk_badge_color(risk_level: str) -> str:
    mapping = {
        "High": "#FEE2E2",
        "Medium": "#FEF3C7",
        "Low": "#D1FAE5",
        "Healthy": "#D1FAE5",
    }
    return mapping.get(risk_level, "#E5E7EB")
