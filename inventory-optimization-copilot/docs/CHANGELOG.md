# Changelog — Inventory Optimization Copilot

All notable changes to this product are documented here. Versioning follows [Semantic Versioning](https://semver.org/) for the workbook product (not PyPI releases).

---

## [2.0.0] — 2026-07-06

### Initial release — Phase 1 (Prompt 01)

First inventory-only production release on branch `feature/inventory-optimization-copilot`, split from the combined toolkit baseline.

#### Added

- **Product identity:** Inventory Optimization Copilot v2.0.0
- **Output:** `dist/Inventory_Optimization_Copilot.xlsx`
- **Deterministic generation:** `RANDOM_SEED=42`, `AS_OF_DATE=2026-07-01`
- **Architecture layers:**
  - `src/domain/` — schemas and shared constants
  - `src/services/` — business logic (status, KPIs, planners, summary)
  - `src/sheets/` — presentation-only sheet builders
  - `src/workbook/` — builder, styles, formulas, charts
  - `src/data_generation/` — fictional inventory CSV generator
- **Phase 1 workbook tabs (7):**
  1. README
  2. Master Inventory
  3. Inventory Dashboard
  4. Aged Excess Analysis
  5. Markdown Planner
  6. Transfer Planner
  7. Management Summary
- **Services:**
  - `inventory_metrics` — sell-through, margin, status/action assignment
  - `inventory_health_service` — aged/excess analysis DataFrame
  - `kpi_service` / `kpi_dashboard_service` — dashboard KPIs and aggregations
  - `markdown_service` — markdown planner with recovery modeling
  - `transfer_service` — network transfer recommendations
  - `summary_service` — management summary content
- **Dataset:** `data/generated/inventory_data.csv` (~120 rows, auto-parts catalog)
- **Quality gate:** pytest, ruff, black, mypy, CI workflow
- **Documentation:** PRD, specs, architecture, business rules, data dictionary, demo script

#### Removed (from combined toolkit source)

- IT-oriented data generators and sheet builders
- Non-inventory workbook tabs from the separation scope
- Legacy combined product naming in user-facing labels

#### Phase 1 scope boundaries

**In scope:**

- Inventory health classification and recommended actions
- Executive dashboard with 10 KPIs and 5 charts
- Transfer-before-markdown planning with net-benefit gate
- Markdown disposition modeling with margin impact
- Printable management summary (inventory-only)

**Planned (not in v2.0.0):**

- Inventory Classification (Prompt 04)
- Cycle Count Plan (Prompt 05)
- Replenishment Planning (Prompt 06)
- Demand Forecast (Prompt 07)
- Service Level Analysis (Prompt 08)
- Purchase Order Tracker (Prompt 08)
- Vendor Scorecards (Prompt 09)

Final contract: **14 sheets** with seven Phase 1 tabs plus seven planned tabs inserted before Management Summary.

---

## Upcoming (unreleased)

### [2.1.0] — Planned

- Inventory Classification sheet + ABC/XYZ service
- Extended tests and data dictionary entries

### [2.2.0] — Planned

- Cycle Count Plan + replenishment parameters
- PO sample dataset

### [2.3.0] — Planned

- Demand Forecast, Service Level Analysis, Purchase Order Tracker, Vendor Scorecards
- Full 14-tab workbook order

---

## Related Documents

- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)
- [BRANCH_SEPARATION.md](BRANCH_SEPARATION.md)
