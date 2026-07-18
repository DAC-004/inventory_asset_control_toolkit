# Branch Separation — Inventory Optimization Copilot

**Date:** 2026-07-06  
**Repository:** `DAC-004/inventory_asset_control_toolkit`

## Purpose

Split the combined inventory + IT toolkit into two independent production products without modifying historical baseline branches. This document records the inventory-only separation performed in Prompt 01.

## Branches

| Branch | Role | Modified in this work? |
|--------|------|------------------------|
| `main` | Combined toolkit baseline | No — preserved |
| `feature/mavis-ai-inventory-copilot` | Inventory-oriented source baseline (+ Streamlit co-pilot app) | No — preserved |
| `feature/inventory-optimization-copilot` | **New** inventory-only production product | Yes — built here |
| `feature/it-asset-control-toolkit` | Future IT-only product | Not created yet |

## Source and Creation

```bash
git switch feature/mavis-ai-inventory-copilot
git pull --ff-only origin feature/mavis-ai-inventory-copilot
git switch -c feature/inventory-optimization-copilot
```

The new product lives in `inventory-optimization-copilot/` (copied from `inventory-it-asset-toolkit/` on the source branch, then IT scope removed).

## Product Identity

| Field | Value |
|-------|-------|
| Product name | Inventory Optimization Copilot |
| Version | v2.0.0 |
| Workbook | `dist/Inventory_Optimization_Copilot.xlsx` |
| Random seed | `42` |
| As-of date | `2026-07-01` |

User-facing labels must not contain the word **Mavis**. The old source branch name appears only in this migration document.

## Dependency Map (Pre-Separation)

```text
src/main.py
  └── generate_inventory.py          [INVENTORY — kept]
  └── generate_it_assets.py            [IT — removed]
  └── generate_software.py             [IT — removed]
  └── generate_mobile.py               [IT — removed]
  └── generate_disposal.py             [IT — removed]
  └── workbook/builder.py              [SHARED — kept, inventory builders only]

workbook/builder.py → SHEET_BUILDERS
  ├── readme_sheet.py                  [SHARED — rewritten, inventory-only]
  ├── master_inventory_sheet.py        [INVENTORY — kept]
  ├── inventory_dashboard_sheet.py     [INVENTORY — kept]
  ├── aged_excess_sheet.py             [INVENTORY — kept]
  ├── markdown_planner_sheet.py        [INVENTORY — kept]
  ├── transfer_planner_sheet.py        [INVENTORY — kept]
  ├── management_summary_sheet.py      [INVENTORY — rewritten, no IT KPIs]
  ├── it_asset_register_sheet.py       [IT — removed]
  ├── audit_reconciliation_sheet.py    [IT — removed]
  ├── software_licenses_sheet.py       [IT — removed]
  ├── mobile_provisioning_sheet.py     [IT — removed]
  └── disposal_log_sheet.py            [IT — removed]

config/workbook_config.py              [SHARED — updated identity + 7-sheet order]
config/style_config.py                 [SHARED — kept; unused IT risk maps remain]
src/workbook/{styles,charts,formulas,utils,validations}.py  [SHARED — IT validations removed]
```

## Removed IT Scope (New Branch Only)

### Data generators

- `generate_it_assets.py`
- `generate_software.py`
- `generate_mobile.py`
- `generate_disposal.py`

### Sheet builders

- `it_asset_register_sheet.py`
- `audit_reconciliation_sheet.py`
- `software_licenses_sheet.py`
- `mobile_provisioning_sheet.py`
- `disposal_log_sheet.py`

### Generated datasets (no longer produced)

- `it_asset_data.csv`
- `software_license_data.csv`
- `mobile_data.csv`
- `disposal_data.csv`

### Workbook tabs (must not appear)

- IT Asset Register
- Audit Reconciliation
- Software Licenses
- Mobile Provisioning
- Disposal Log

### Tests removed or rewritten

- IT-specific imports in `test_requirements.py`, `test_spec_requirements.py`
- IT validation tests in `test_workbook_utils.py`
- IT sheet presence assertions replaced with negative checks

## Preserved Inventory Scope

### Phase 1 sheet order

1. README  
2. Master Inventory  
3. Inventory Dashboard  
4. Aged Excess Analysis  
5. Markdown Planner  
6. Transfer Planner  
7. Management Summary  

### Capabilities

- Fictional inventory data generation (seed 42)
- Inventory status, aged/excess analysis, transfer planning, markdown modeling
- Inventory dashboard KPIs and charts
- Printable management summary (inventory KPIs only)

## Future IT Branch

IT Asset Control functionality will be developed on:

```text
feature/it-asset-control-toolkit
```

Do not merge inventory and IT products until each is independently complete.

## Verification Commands

Run from `inventory-optimization-copilot/`:

```bash
python -m compileall src config
pytest -q
python src/main.py
```

Open with openpyxl:

```python
from openpyxl import load_workbook
wb = load_workbook("dist/Inventory_Optimization_Copilot.xlsx", read_only=True)
assert wb.sheetnames == [
    "README", "Master Inventory", "Inventory Dashboard",
    "Aged Excess Analysis", "Markdown Planner",
    "Transfer Planner", "Management Summary",
]
assert "IT Asset Register" not in wb.sheetnames
wb.close()
```

Full quality gate (Prompt 01+):

```bash
ruff check .
black --check .
mypy src config
pytest --cov=src --cov-report=term-missing -q
```

## Acceptance Checklist

- [x] Branch `feature/inventory-optimization-copilot` exists locally and remotely
- [x] `main` and `feature/mavis-ai-inventory-copilot` unchanged
- [x] Workbook builds as `Inventory_Optimization_Copilot.xlsx`
- [x] No IT sheets or IT datasets
- [x] Tests pass
- [x] Separation commit pushed only to the new branch
