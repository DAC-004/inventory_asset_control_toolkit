# Inventory Optimization Copilot — Technical Specification

**Version:** v2.0.0  
**Output:** `dist/Inventory_Optimization_Copilot.xlsx`

## 1. Technical Overview

Python 3.11+ application that generates a professional Excel workbook for inventory optimization using `openpyxl` and `pandas`. The build is deterministic, modular, and reproducible from source.

## 2. Tech Stack

| Layer | Choice |
|-------|--------|
| Language | Python 3.11+ |
| Excel | openpyxl |
| Data | pandas, numpy, faker |
| Quality | pytest, black, ruff, mypy |

No web framework, database, VBA, macros, or external ERP integration.

## 3. Project Structure

```text
inventory-optimization-copilot/
├── config/workbook_config.py
├── src/
│   ├── main.py
│   ├── data_generation/generate_inventory.py
│   ├── business_rules/
│   ├── sheets/
│   ├── workbook/builder.py
│   └── tests/
├── data/generated/inventory_data.csv
└── dist/Inventory_Optimization_Copilot.xlsx
```

## 4. Deterministic Constants

```python
RANDOM_SEED = 42
AS_OF_DATE = date(2026, 7, 1)
VERSION = "v2.0.0"
```

## 5. Sheet Order (phase 1)

1. README  
2. Master Inventory  
3. Inventory Dashboard  
4. Aged Excess Analysis  
5. Markdown Planner  
6. Transfer Planner  
7. Management Summary  

## 6. Inventory Record Schema

| Column | Type | Notes |
|--------|------|-------|
| item_id | string | Primary key |
| sku | string | |
| product_name | string | Fictional brands only |
| category | string | |
| warehouse | string | |
| on_hand_qty | int | ≥ 0 |
| unit_cost | float | ≥ 0 |
| unit_price | float | ≥ 0 |
| avg_daily_demand | float | ≥ 0 |
| days_since_last_sale | int | ≥ 0 |
| inventory_status | string | Derived in Python |
| recommended_action | string | Derived in Python |

## 7. Business Rules

### 7.1 Inventory status (first match wins)

| Status | Rule |
|--------|------|
| Obsolete | age ≥ 365 days |
| Excess / Aged | age ≥ 180 and excess pattern |
| Slow-Moving | age ≥ 180 and low sell-through |
| Excess | excess qty pattern |
| Stockout Risk | low cover vs demand |
| Healthy | default |

### 7.2 Markdown planner

Age bands map to markdown % and disposition (Hold, 10%, 20%, Liquidate).

### 7.3 Transfer planner

Recommend transfer when destination demand buffer justifies moving excess from source warehouse.

## 8. Calculation Policy

1. Compute KPIs in Python.  
2. Write calculated values into tables.  
3. Use Excel formulas sparingly for transparency.  
4. Set workbook recalculation properties.  
5. Test Python-computed values in pytest.  
6. Never require Excel to open the file for correctness.

## 9. Build Command

```bash
python src/main.py
```

## 10. Quality Gate

```bash
python -m compileall src config
ruff check .
black --check .
mypy src config
pytest --cov=src --cov-report=term-missing -q
python src/main.py
```

## 11. Out of Scope

This product excludes IT Asset Register, Audit Reconciliation, Software Licenses, Mobile Provisioning, and Disposal Log (future IT Asset Control Toolkit branch).

## 12. Future Sheets (prompts 04–09)

Inventory Classification, Cycle Count Plan, Replenishment Planning, Demand Forecast, Service Level Analysis, Purchase Order Tracker, Vendor Scorecards.
