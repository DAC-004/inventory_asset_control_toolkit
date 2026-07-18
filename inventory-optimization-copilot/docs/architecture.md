# Inventory Optimization Copilot — Architecture

**Version:** v2.0.0  
**Output:** `dist/Inventory_Optimization_Copilot.xlsx`

## Overview

Python application that generates a deterministic Excel workbook for inventory optimization. Data is generated in pandas, business rules run in Python, and `openpyxl` writes tables, charts, and formatting.

## Module Layout

```text
inventory-optimization-copilot/
├── config/
│   └── workbook_config.py      # VERSION, AS_OF_DATE, RANDOM_SEED, SHEET_ORDER
├── data/generated/               # CSV exports (gitignored output)
├── dist/                         # Workbook output
├── src/
│   ├── main.py                   # CLI entry point
│   ├── data_generation/
│   │   └── generate_inventory.py
│   ├── business_rules/           # Status, markdown, transfer logic
│   ├── sheets/                   # One module per workbook tab
│   ├── workbook/
│   │   └── builder.py            # Orchestrates sheet builders
│   └── tests/
├── build.sh / build.bat
└── requirements.txt
```

## Data Flow

1. `main.py` calls `generate_inventory_data()` with `RANDOM_SEED` and row count from config.
2. CSV is saved to `data/generated/inventory_data.csv`.
3. `build_workbook()` passes a context dict to each sheet builder in `SHEET_ORDER`.
4. Workbook is written to `dist/Inventory_Optimization_Copilot.xlsx`.

## Sheet Builders (phase 1)

| Sheet | Module | Data source |
|-------|--------|-------------|
| README | `readme_sheet.py` | Static content |
| Master Inventory | `master_inventory_sheet.py` | `context["data"]["inventory"]` |
| Inventory Dashboard | `inventory_dashboard_sheet.py` | Aggregated KPIs |
| Aged Excess Analysis | `aged_excess_analysis_sheet.py` | Filtered inventory |
| Markdown Planner | `markdown_planner_sheet.py` | Markdown rules |
| Transfer Planner | `transfer_planner_sheet.py` | Transfer rules |
| Management Summary | `management_summary_sheet.py` | Cross-sheet KPIs |

## Deterministic Build

Central constants in `config/workbook_config.py`:

```python
RANDOM_SEED = 42
AS_OF_DATE = date(2026, 7, 1)
VERSION = "v2.0.0"
```

## Calculation Policy

`openpyxl` writes formulas but does not evaluate them. Operational KPIs are computed in Python and written as values. Excel formulas are used only when formula visibility adds value for the demo audience.

## Extension Points (prompts 04–09)

Additional generators and sheet builders will plug into the same `build_workbook()` pipeline and extend `SHEET_ORDER` without changing historical baseline branches.
