# Inventory Optimization Copilot

**Version:** v2.0.0 · **Author:** Daniel A. Cruz

Python project that generates a professional, interview-ready Excel workbook for **inventory optimization** — aged and excess analysis, transfer planning, markdown recommendations, and executive reporting.

> All sample data is **fictional** and safe for portfolio and interview demos.

## Quick Start

```bash
cd inventory-optimization-copilot
pip install -r requirements.txt
./build.sh          # macOS / Linux  (or: build.bat on Windows)
```

Output: `dist/Inventory_Optimization_Copilot.xlsx`

## Workbook Tabs (v2.0.0 phase 1)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | README | Product guide and demo path |
| 2 | Master Inventory | Operational inventory dataset |
| 3 | Inventory Dashboard | Leadership KPIs and charts |
| 4 | Aged Excess Analysis | Exception inventory |
| 5 | Markdown Planner | Markdown and disposition modeling |
| 6 | Transfer Planner | Network transfer recommendations |
| 7 | Management Summary | Printable executive overview |

**Planned in prompts 04–09:** Inventory Classification, Cycle Count Plan, Replenishment Planning, Demand Forecast, Service Level Analysis, Purchase Order Tracker, Vendor Scorecards.

## Branch

This product lives on:

```text
feature/inventory-optimization-copilot
```

Historical baselines (`main`, `feature/mavis-ai-inventory-copilot`) are preserved unchanged.

## Tests

```bash
pytest -q
python src/main.py
```

## Documentation

- [PRD.md](PRD.md) — product requirements
- [specs.md](specs.md) — technical specification
- [docs/architecture.md](docs/architecture.md) — module layout
