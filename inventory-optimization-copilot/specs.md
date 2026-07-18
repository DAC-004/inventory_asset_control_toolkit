# Inventory Optimization Copilot — Technical Specification

**Version:** v2.0.0  
**Branch:** `feature/inventory-optimization-copilot`  
**Output:** `dist/Inventory_Optimization_Copilot.xlsx`

---

## 1. Technical Overview

Python 3.11+ application that generates a professional Excel workbook for inventory optimization using `openpyxl` and `pandas`. The build is deterministic, modular, and reproducible from source.

**Architecture principle:** Business logic in `src/services/`; sheet builders in `src/sheets/` handle presentation only.

---

## 2. Tech Stack

| Layer | Choice |
|-------|--------|
| Language | Python 3.11+ |
| Excel | openpyxl |
| Data | pandas, numpy, faker, python-dateutil |
| Quality | pytest, pytest-cov, black, ruff, mypy |

No web framework, database, VBA, macros, or external ERP integration.

---

## 3. Project Structure

```text
inventory-optimization-copilot/
├── README.md
├── prd.md
├── specs.md
├── requirements.txt
├── pyproject.toml
├── build.sh / build.bat
├── config/
│   ├── workbook_config.py      # Paths, version, thresholds, SHEET_ORDER
│   └── style_config.py         # Colors, fonts, formats
├── data/generated/
│   └── inventory_data.csv
├── dist/
│   └── Inventory_Optimization_Copilot.xlsx
├── docs/
│   ├── ARCHITECTURE.md
│   ├── BUSINESS_RULES.md
│   ├── DATA_DICTIONARY.md
│   └── ...
└── src/
    ├── main.py
    ├── domain/
    │   ├── constants.py
    │   └── schemas.py
    ├── data_generation/
    │   └── generate_inventory.py
    ├── services/               # ★ Business logic
    │   ├── inventory_metrics.py
    │   ├── inventory_health_service.py
    │   ├── kpi_service.py
    │   ├── kpi_dashboard_service.py
    │   ├── markdown_service.py
    │   ├── transfer_service.py
    │   └── summary_service.py
    ├── sheets/                   # Presentation
    │   ├── readme_sheet.py
    │   ├── master_inventory_sheet.py
    │   ├── inventory_dashboard_sheet.py
    │   ├── aged_excess_sheet.py
    │   ├── markdown_planner_sheet.py
    │   ├── transfer_planner_sheet.py
    │   └── management_summary_sheet.py
    ├── workbook/
    │   ├── builder.py
    │   ├── styles.py
    │   ├── formulas.py
    │   ├── charts.py
    │   ├── validations.py
    │   └── utils.py
    └── tests/
```

---

## 4. Deterministic Constants

Defined in `config/workbook_config.py`:

```python
RANDOM_SEED = 42
AS_OF_DATE = date(2026, 7, 1)
VERSION = "v2.0.0"
WORKBOOK_TITLE = "Inventory Optimization Copilot"
OUTPUT_FILENAME = "Inventory_Optimization_Copilot.xlsx"
```

---

## 5. Sheet Order

v2.0.0 implements all **14 sheets**:

1. README  
2. Master Inventory  
3. Inventory Dashboard  
4. Inventory Classification  
5. Aged Excess Analysis  
6. Cycle Count Plan  
7. Replenishment Planning  
8. Transfer Planner  
9. Markdown Planner  
10. Demand Forecast  
11. Service Level Analysis  
12. Purchase Order Tracker  
13. Vendor Scorecards  
14. Management Summary  

Configured via `SHEET_ORDER` in `workbook_config.py`.

---

## 6. Data Model

### 6.1 Inventory record

22 columns — see `src/domain/schemas.py` → `INVENTORY_COLUMN_ORDER` and [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md).

| Column | Type | Notes |
|--------|------|-------|
| item_id | string | Primary key |
| sku | string | |
| product_name | string | Fictional brands only |
| category / subcategory | string | |
| location / location_type / region | string | |
| quantity_on_hand | int | ≥ 0 |
| min_stock / max_stock | int | |
| unit_cost / selling_price | float | ≥ 0 |
| total_value | float | qty × unit_cost |
| last_movement_date / last_sale_date | date | |
| age_days | int | From AS_OF_DATE |
| demand_90_day | int | ≥ 0 |
| sell_through_rate | float | 0–1 |
| gross_margin_pct | float | 0–1 |
| status | string | Service-derived |
| recommended_action | string | Service-derived |

### 6.2 Generated CSV

- Path: `data/generated/inventory_data.csv`
- Rows: default 120 (`ROW_COUNTS["inventory"]["default"]`)
- Generator: `generate_inventory_data(row_count, seed)`

---

## 7. Services Layer

| Module | Responsibility |
|--------|----------------|
| `inventory_metrics` | Sell-through, margin, status/action assignment |
| `inventory_health_service` | Aged/excess analysis DataFrame, risk mapping |
| `kpi_service` | Excel formula KPI definitions for dashboard/summary |
| `kpi_dashboard_service` | Location/status/aging/action aggregations, top excess |
| `markdown_service` | Markdown planner rows, recovery, margin impact |
| `transfer_service` | Transfer candidates, costs, net benefit |
| `summary_service` | Management summary risks and action counts |

**Constraint:** Services must not import openpyxl.

---

## 8. Business Rules

Authoritative definitions: [docs/BUSINESS_RULES.md](docs/BUSINESS_RULES.md).

### 8.1 Inventory status (first match wins)

| Status | Rule |
|--------|------|
| Stockout Risk | qty < min_stock |
| Obsolete | age > 365 and demand_90_day = 0 |
| Excess / Aged | qty > max_stock and age > 180 |
| Excess | qty > max_stock |
| Slow-Moving | age > 180 and sell_through < 0.15 |
| Healthy | default |

### 8.2 Markdown planner

Age bands → markdown % and disposition (Hold, Transfer First, 10%, 20%, Liquidate).

### 8.3 Transfer planner

Recommend when source excess, destination need, suggested qty > 0, net benefit > 0.

---

## 9. Workbook Builder

`src/workbook/builder.py`:

```python
SHEET_BUILDERS = {
    "README": readme_sheet.build,
    "Master Inventory": master_inventory_sheet.build,
    "Inventory Dashboard": inventory_dashboard_sheet.build,
    "Aged Excess Analysis": aged_excess_sheet.build,
    "Markdown Planner": markdown_planner_sheet.build,
    "Transfer Planner": transfer_planner_sheet.build,
    "Management Summary": management_summary_sheet.build,
}
```

Build flow:

1. `create_workbook()` — metadata, remove default sheet  
2. For each name in `SHEET_ORDER`, invoke builder with `context = {"data": datasets, "workbook": wb}`  
3. `wb.save(WORKBOOK_PATH)`

---

## 10. Calculation Policy

1. Compute KPIs and planner rows in Python services.  
2. Write calculated values into tables.  
3. Use Excel formulas sparingly for dashboard/summary transparency (`kpi_service`).  
4. Set workbook recalculation properties where applicable.  
5. Test Python-computed values in pytest.  
6. Never require Excel to open the file for build correctness.

---

## 11. Styling

Centralized in `config/style_config.py` and applied via `src/workbook/styles.py`:

- Header fills and fonts  
- KPI card layout  
- Risk color mapping (High/Medium/Low)  
- Number formats: currency, percentage, integer, date  

---

## 12. Build Command

```bash
python src/main.py
```

Steps logged:

1. Create `dist/` and `data/generated/`  
2. Generate inventory CSV  
3. Build workbook  
4. Verify output exists  

---

## 13. Quality Gate

```bash
python -m compileall src config
ruff check .
black --check .
mypy src config
pytest --cov=src --cov-report=term-missing -q
python src/main.py
```

CI: `.github/workflows/ci.yml`

---

## 14. Testing Requirements

| Test module | Coverage |
|-------------|----------|
| `test_data_generation` | Seed, columns, status coverage |
| `test_workbook_build` | End-to-end build |
| `test_required_sheets` | Tab names and order |
| `test_*_sheet` | Per-sheet structure |
| `test_requirements` | Product identity guards |
| `test_spec_requirements` | Spec compliance |

---

## 15. Extension Guide (Planned Sheets)

For each new tab (prompts 04–09):

1. Add `src/services/<feature>_service.py`  
2. Add `src/sheets/<feature>_sheet.py`  
3. Register in `SHEET_BUILDERS` and `SHEET_ORDER`  
4. Extend data generation if new CSV required  
5. Add tests and update docs  

---

## 16. Out of Scope

This product excludes enterprise asset-control workbook tabs and generators that belong to the future IT-only branch. See [docs/BRANCH_SEPARATION.md](docs/BRANCH_SEPARATION.md).

Not in scope:

- Live AI / LLM integration  
- Real ERP connectivity  
- Macros or VBA  

---

## 17. Related Documents

- [prd.md](prd.md) — product requirements  
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — architecture detail  
- [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) — field definitions  
- [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) — release verification  
