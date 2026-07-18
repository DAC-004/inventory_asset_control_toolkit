# Requirements Checklist — Inventory Optimization Copilot v2.0.0

## Branch & Identity

| Requirement | Status |
|-------------|--------|
| Branch `feature/inventory-optimization-copilot` | ✅ |
| Product name: Inventory Optimization Copilot | ✅ |
| Workbook: `Inventory_Optimization_Copilot.xlsx` | ✅ |
| No "Mavis" in user-facing labels | ✅ |
| No IT sheets in workbook | ✅ |

## Phase 1 Sheets

| Sheet | Status |
|-------|--------|
| README | ✅ |
| Master Inventory | ✅ |
| Inventory Dashboard | ✅ |
| Aged Excess Analysis | ✅ |
| Markdown Planner | ✅ |
| Transfer Planner | ✅ |
| Management Summary | ✅ |

## Build & Quality

| Check | Command |
|-------|---------|
| Compile | `python -m compileall src config` |
| Lint | `ruff check .` |
| Format | `black --check .` |
| Types | `mypy src config` |
| Tests | `pytest --cov=src --cov-report=term-missing -q` |
| Workbook | `python src/main.py` |

## Planned (prompts 04–09)

- Inventory Classification  
- Cycle Count Plan  
- Replenishment Planning  
- Demand Forecast  
- Service Level Analysis  
- Purchase Order Tracker  
- Vendor Scorecards  
