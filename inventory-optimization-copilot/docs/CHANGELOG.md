# Changelog — Inventory Optimization Copilot

All notable changes to this product are documented here. Versioning follows [Semantic Versioning](https://semver.org/) for the workbook product (not PyPI releases).

---

## [2.0.0] — 2026-07-18

### Production release — full 14-sheet inventory workbook

Portfolio-ready release on branch `feature/inventory-optimization-copilot`.

#### Added

- **Product identity:** Inventory Optimization Copilot v2.0.0
- **Output:** `dist/Inventory_Optimization_Copilot.xlsx`
- **Deterministic generation:** `RANDOM_SEED=42`, `AS_OF_DATE=2026-07-01`
- **14 workbook tabs:**
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
- **Eight fictional datasets** under `data/generated/`
- **Services:** classification, cycle count, replenishment, forecast, service level, PO tracker, vendor scorecards, transfer optimization, markdown optimization, KPI dashboard, management summary
- **Executive dashboard:** 27 KPIs, 10 charts, four analytic sections
- **Production hardening:** structured logging, atomic workbook writes, post-save validation, custom exceptions, CI workflow with coverage gate
- **Documentation:** PRD, specs, architecture, business rules, data dictionary, demo script, release checklist

#### Removed (from combined toolkit source)

- IT-oriented data generators and sheet builders
- Non-inventory workbook tabs from the separation scope
- Legacy combined product naming in user-facing labels

---

## Related Documents

- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)
- [BRANCH_SEPARATION.md](BRANCH_SEPARATION.md)
