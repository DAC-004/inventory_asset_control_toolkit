# Inventory Optimization Copilot — Product Requirements Document

**Version:** v2.0.0  
**Branch:** `feature/inventory-optimization-copilot`  
**Output:** `dist/Inventory_Optimization_Copilot.xlsx`  
**As-of date:** 2026-07-01 · **Random seed:** 42

---

## 1. Product Summary

**Inventory Optimization Copilot** is a Python-generated Excel workbook that demonstrates inventory health analysis, transfer and markdown planning, and executive reporting for supply chain and warehouse decision support.

The term **Copilot** refers to structured recommendations, prioritization, and management guidance embedded in the workbook — **not** a live AI model, chat interface, or external API. All logic is deterministic Python code executed at build time.

All sample data is **fictional**, reproducible, and safe for portfolio and interview demos.

---

## 2. Target Users

| Persona | Needs |
|---------|-------|
| Inventory / supply chain analyst | Exception lists, aging analysis, action prioritization |
| Procurement & distribution manager | Transfer vs. markdown trade-offs, replenishment signals |
| Warehouse / DC supervisor | Location-level stock balance, cycle count priorities |
| Executive stakeholder | Dashboard KPIs, printable management summary |

---

## 3. Business Objectives

1. Surface aged, excess, slow-moving, obsolete, and stockout-risk inventory.
2. Recommend **transfer before markdown** when network economics justify movement.
3. Model markdown and liquidation paths with margin and recovery awareness.
4. Provide leadership-ready dashboards and a one-page management summary.
5. Demonstrate production-quality Python + Excel automation for interview and portfolio use.

---

## 4. User Stories

| ID | Story | Phase |
|----|-------|-------|
| US-01 | As an analyst, I want a master inventory dataset with derived status and recommended actions so I can triage exceptions quickly. | 1 ✅ |
| US-02 | As a manager, I want dashboard KPIs and charts so I can assess portfolio health in one view. | 1 ✅ |
| US-03 | As an analyst, I want an aged/excess exception report with risk levels and analyst notes. | 1 ✅ |
| US-04 | As a planner, I want markdown scenarios with recovery and margin impact before approving price cuts. | 1 ✅ |
| US-05 | As a DC manager, I want transfer recommendations with net benefit so I move stock before discounting. | 1 ✅ |
| US-06 | As an executive, I want a printable summary of top risks and recommended actions. | 1 ✅ |
| US-07 | As an analyst, I want ABC/XYZ classification to focus attention on high-value movers. | Planned |
| US-08 | As a warehouse lead, I want a cycle count plan prioritized by value and risk. | Planned |
| US-09 | As a buyer, I want replenishment parameters (safety stock, ROP, EOQ) and projected availability. | Planned |
| US-10 | As a planner, I want demand forecast and service-level views for stocking decisions. | Planned |
| US-11 | As procurement, I want PO tracking and vendor scorecards for supplier performance. | Planned |

---

## 5. Workbook Contract — 14 Sheets

### Final tab order (target contract)

| # | Sheet | Phase | Prompt |
|---|-------|-------|--------|
| 1 | README | **Phase 1 ✅** | 01 |
| 2 | Master Inventory | **Phase 1 ✅** | 01 |
| 3 | Inventory Dashboard | **Phase 1 ✅** | 01 |
| 4 | Inventory Classification | Planned | 04 |
| 5 | Aged Excess Analysis | **Phase 1 ✅** | 01 |
| 6 | Cycle Count Plan | Planned | 05 |
| 7 | Replenishment Planning | Planned | 06 |
| 8 | Transfer Planner | **Phase 1 ✅** | 01 |
| 9 | Markdown Planner | **Phase 1 ✅** | 01 |
| 10 | Demand Forecast | Planned | 07 |
| 11 | Service Level Analysis | Planned | 08 |
| 12 | Purchase Order Tracker | Planned | 08 |
| 13 | Vendor Scorecards | Planned | 09 |
| 14 | Management Summary | **Phase 1 ✅** | 01 |

Phase 1 ships **7 sheets** in this order (Classification and intermediate planning tabs deferred):

README → Master Inventory → Inventory Dashboard → Aged Excess Analysis → Markdown Planner → Transfer Planner → Management Summary.

Prompts 04–09 insert the seven planned tabs between Transfer Planner and Management Summary per `config/workbook_config.py`.

---

## 6. Sheet Requirements

### 6.1 README — Phase 1 ✅

**Purpose:** Onboarding for reviewers and interviewers.

**Must include:** product title, version, fictional-data disclaimer, 10-minute demo path, tab navigation, build instructions reference, Copilot definition (decision support, not live AI).

---

### 6.2 Master Inventory — Phase 1 ✅

**Purpose:** Canonical operational dataset for all inventory analytics.

**Fields:** See [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md).

**Derived logic:**

- `total_value = quantity_on_hand × unit_cost`
- `age_days = AS_OF_DATE − last_sale_date` (minimum 0)
- `sell_through_rate`, `gross_margin_pct`, `status`, `recommended_action` computed in Python services

**Acceptance:** Every status and recommended-action label appears at least once in generated data (seed 42).

---

### 6.3 Inventory Dashboard — Phase 1 ✅

**Purpose:** Executive visibility into inventory health.

**KPI cards (10):** Total Inventory Value, Aged Inventory Value, Excess Inventory Value, Slow-Moving SKU Count, Obsolete SKU Count, Transfer Candidate Count, Markdown Candidate Count, Stockout Risk Count, Estimated Recovery Value, Average Gross Margin %.

**Charts (5):** Value by Location, Status Breakdown, Aging Buckets, Recommended Action Summary, Top 10 Excess Items.

**Design:** Large KPI cards, section headers, consistent palette from `config/style_config.py`, no clutter.

---

### 6.4 Inventory Classification — Planned (Prompt 04)

**Purpose:** ABC/XYZ (or ABC-only MVP) segmentation for prioritization.

**Required fields:** SKU, Product Name, Category, Location, Annual Usage Value, Cumulative %, ABC Class, Demand Variability (XYZ), Combined Segment, Recommended Review Frequency.

**Rules:** ABC by Pareto on usage value; XYZ by coefficient of variation on demand; combined segment drives review cadence.

---

### 6.5 Aged Excess Analysis — Phase 1 ✅

**Purpose:** Exception report for non-healthy inventory (risk level ≠ Low).

**Fields:** SKU, Product Name, Location, Quantity On Hand, Max Stock, Excess Quantity, Age Days, 90 Day Demand, Sell Through Rate, Inventory Value, Risk Level, Issue Type, Recommended Action, Analyst Notes.

**Sort:** Risk level (High → Low), then Inventory Value descending.

---

### 6.6 Cycle Count Plan — Planned (Prompt 05)

**Purpose:** Prioritized physical count schedule by location and SKU risk.

**Fields:** Location, SKU, ABC Class, Last Count Date, Days Since Count, Inventory Value, Risk Level, Count Priority, Scheduled Count Week, Counter Assignee (fictional).

**Rules:** High-value + high-risk SKUs counted more frequently; never-counted or stale counts elevated.

---

### 6.7 Replenishment Planning — Planned (Prompt 06)

**Purpose:** Parameter-driven reorder guidance.

**Fields:** SKU, Location, On Hand, Min/Max Stock, Avg Daily Demand, Lead Time Days, Safety Stock, Reorder Point, EOQ, Projected Stockout Date, Suggested Order Qty, Order By Date.

**Logic:** Standard inventory formulas (see KPI section); flag lines where projected availability < lead time + safety stock.

---

### 6.8 Transfer Planner — Phase 1 ✅

**Purpose:** Network transfer recommendations before markdown.

**Fields:** SKU, Product Name, Source/Destination Location, quantities, destination min stock & demand, suggested transfer qty, unit cost, transfer cost, estimated margin protected, net benefit, recommendation.

**Gate:** Include row only when source has excess, destination needs stock, suggested qty > 0, and **net benefit > 0**.

---

### 6.9 Markdown Planner — Phase 1 ✅

**Purpose:** Price-reduction and disposition modeling for eligible statuses.

**Eligible statuses:** Slow-Moving, Excess, Excess / Aged, Obsolete.

**Fields:** SKU through Recommended Disposition (see data dictionary).

**Dispositions:** Hold, Transfer First, 10% Markdown, 20% Markdown, Liquidate (30% markdown path).

---

### 6.10 Demand Forecast — Planned (Prompt 07)

**Purpose:** Simple forward demand projection by SKU/location.

**Fields:** SKU, Location, Historical 90-Day Demand, Forecast Method, Forecast Periods (W+1…W+12), Seasonality Index, Forecast Confidence, Notes.

**Method (MVP):** Moving average or seasonal naive from master demand history.

---

### 6.11 Service Level Analysis — Planned (Prompt 08)

**Purpose:** Fill-rate and service-level performance vs. targets.

**Fields:** SKU, Location, Target Service Level %, Actual Fill Rate %, Stockout Events, Lost Sales Units (est.), Days Below Min Stock, Service Level Gap, Action.

---

### 6.12 Purchase Order Tracker — Planned (Prompt 08)

**Purpose:** Open PO visibility and receipt timing.

**Fields:** PO Number, Vendor, SKU, Order Qty, Received Qty, Open Qty, Order Date, Expected Receipt, Status, Days Late, Buyer.

---

### 6.13 Vendor Scorecards — Planned (Prompt 09)

**Purpose:** Supplier performance summary.

**Fields:** Vendor, On-Time Delivery %, Fill Rate %, Quality Accept Rate %, Avg Lead Time Days, YTD Spend, Score (weighted), Tier, Review Action.

---

### 6.14 Management Summary — Phase 1 ✅

**Purpose:** Printable one-page executive overview (inventory only in Phase 1).

**Sections:** Header metadata, KPI row (5 metrics), top inventory risks (top 5), recommended action counts, narrative callouts, 30/60/90-day action placeholders.

---

## 7. Datasets

| Dataset | File | Rows (default) | Phase |
|---------|------|----------------|-------|
| Master inventory | `data/generated/inventory_data.csv` | 120 | 1 ✅ |
| Purchase orders | `data/generated/purchase_orders.csv` | TBD | Planned |
| Vendors | `data/generated/vendors.csv` | TBD | Planned |
| Demand history | derived from master | — | Planned |

**Generation:** `src/data_generation/generate_inventory.py` with `RANDOM_SEED=42`, `AS_OF_DATE=2026-07-01`.

**Catalog:** Auto parts / shop supplies across tires, brake parts, batteries, filters, fluids, tools, shop supplies, accessories. Locations: 3 DCs + 8 retail stores (Northeast / NYC Metro).

---

## 8. KPI & Metric Definitions

All Phase 1 metrics are implemented in `src/services/`. Planned metrics will follow the same service-first pattern.

| Metric | Formula | Period / Unit | Source | Edge Cases |
|--------|---------|---------------|--------|------------|
| **Inventory Value** | `quantity_on_hand × unit_cost` | Point-in-time; USD | Master Inventory | Zero qty → 0 value |
| **Aged Inventory Value** | Sum of `total_value` where `age_days > 180` | As-of date; USD | Dashboard KPI | Inclusive of 181+ days |
| **Excess Inventory Value** | Sum of value where status ∈ {Excess, Excess / Aged} | USD | Dashboard KPI | Uses status, not qty alone |
| **Excess Quantity** | `max(quantity_on_hand − max_stock, 0)` | Units | Aged Excess | Negative clipped to 0 |
| **Age Days** | `AS_OF_DATE − last_sale_date` | Days | Master Inventory | Minimum 0 |
| **Sell-Through Rate** | `demand_90_day / (quantity_on_hand + demand_90_day)` | 90-day; ratio 0–1 | Master Inventory | Denominator 0 → 0; cap at 1.0 |
| **Gross Margin %** | `(selling_price − unit_cost) / selling_price` | Per SKU; ratio | Master Inventory | Price ≤ 0 → 0 |
| **Estimated Recovery Value (dashboard)** | Sum of `total_value` where recommended_action ∈ markdown actions | USD | Dashboard formula | Markdown actions: Markdown Review, Transfer or Markdown, Liquidate |
| **Markdown Recovery (planner)** | `quantity × markdown_price × projected_sell_through` | USD | Markdown Planner | Per eligible row |
| **Margin Impact** | Projected margin $ − current margin $ at sell-through | USD | Markdown Planner | Uses qty × unit economics |
| **Projected Sell-Through** | `min(current_rate + markdown_pct × 0.45, 0.90)` | Ratio | Markdown Planner | No uplift when markdown 0 |
| **Transfer Cost** | Lane-based base + per-unit by DC/store pattern | USD | Transfer Planner | See `transfer_service.py` |
| **Margin Protected** | `suggested_qty × unit_cost × 0.35` | USD | Transfer Planner | Fixed margin rate constant |
| **Net Benefit** | `margin_protected − transfer_cost` | USD | Transfer Planner | Row excluded if ≤ 0 |
| **ABC Class** | Pareto on annual usage value (A≤80%, B≤95%, C remainder) | Rolling 12 mo (est.) | Planned | Usage ≈ `demand_90_day × 4 × unit_cost` |
| **Inventory Turnover** | `annualized_cogs / avg_inventory_value` | Turns/year | Planned | COGS ≈ `demand_90_day × 4 × unit_cost` |
| **Days on Hand (DOH)** | `quantity_on_hand / avg_daily_demand` | Days | Planned | Zero demand → 999 or N/A |
| **Coverage** | `quantity_on_hand / (demand_90_day / 90)` | Days | Planned | Synonym for DOH in replenishment |
| **Cycle Count Accuracy** | `1 − |system_qty − counted_qty| / system_qty` | Per count event | Planned | System qty 0 → skip |
| **Demand (90-day)** | Observed units sold/moved in 90 days | 90 days; units | Master Inventory | Integer ≥ 0 |
| **Safety Stock** | `z × σ_demand × √lead_time` (or rule-based MVP) | Units | Planned | Defaults when σ unknown |
| **Reorder Point** | `(avg_daily_demand × lead_time) + safety_stock` | Units | Planned | — |
| **Projected Availability** | `on_hand + open_po_qty − forecast_demand` over horizon | Units / date | Planned | — |
| **EOQ** | `√(2 × annual_demand × order_cost / holding_cost)` | Units | Planned | Holding cost % of unit cost |
| **Forecast (MVP)** | Moving average of historical demand | Weekly buckets | Planned | — |
| **Fill Rate** | `units_shipped / units_demanded` | Period; % | Planned | Zero demand → 100% or N/A |
| **PO Open Qty** | `order_qty − received_qty` | Units | Planned | — |
| **Vendor On-Time %** | `on_time_deliveries / total_deliveries` | Rolling 90d; % | Planned | — |

---

## 9. Design Requirements

- **Visual:** Executive dashboard aesthetic; navy/teal/slate palette; risk colors (High=red, Medium=amber, Low=green).
- **Typography:** Consistent header and body fonts via `style_config.py`.
- **Numbers:** Currency `$#,##0.00`, percentages `0.0%`, integers `#,##0`.
- **Print:** Management Summary fits one landscape page where possible.
- **Accessibility:** High contrast headers; no reliance on color alone for critical status (text labels required).
- **No macros/VBA/external links.**

---

## 10. Testing & Quality

| Layer | Requirement |
|-------|-------------|
| Unit | Services and metrics tested in `src/tests/` |
| Integration | Workbook builds with exact Phase 1 sheet order |
| Regression | Seed 42 produces stable row counts and status coverage |
| Static analysis | `ruff`, `black`, `mypy` clean |
| Coverage | `pytest --cov=src` on CI |

**Build must succeed without opening Excel.** Excel formulas on dashboard/summary are supplementary transparency; Python is source of truth for generation.

---

## 11. Success Criteria

### Phase 1 (v2.0.0)

- [x] `python src/main.py` produces `dist/Inventory_Optimization_Copilot.xlsx`
- [x] Seven tabs in configured order; no out-of-product tabs
- [x] All inventory statuses and actions represented in data
- [x] `pytest -q` passes
- [x] No prohibited product naming in user-facing content
- [x] Business logic resides in `src/services/`, not sheet builders

### Full contract (future)

- [ ] Fourteen tabs in final order
- [ ] Replenishment and forecast sheets wired to shared demand model
- [ ] PO and vendor datasets generated deterministically

---

## 12. Demo Path (~10 minutes)

See [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md). Summary:

1. README — product framing (1 min)
2. Master Inventory — data model & rules (2 min)
3. Inventory Dashboard — KPIs + charts (2 min)
4. Aged Excess Analysis — exceptions (1.5 min)
5. Transfer Planner — network optimization (2 min)
6. Markdown Planner — recovery modeling (1 min)
7. Management Summary — executive close (0.5 min)

---

## 13. Out of Scope (This Product)

This branch is **inventory-only**. The following capabilities belong to the separate **Enterprise Asset Control Toolkit** (`feature/it-asset-control-toolkit`), not this product:

- Enterprise hardware lifecycle registers and audit reconciliation workflows
- Software entitlement and renewal compliance tracking
- Employee mobile device onboarding and recovery checklists
- Asset retirement, data destruction, and certificate tracking logs
- Live AI chat, LLM integration, or real-time ERP connectivity
- Multi-tenant SaaS deployment

---

## 14. Future Enhancements

- Phase 2 sheets (prompts 04–09): classification through vendor scorecards
- Scenario toggles (aggressive vs. conservative markdown)
- Multi-region deterministic datasets
- Export of action lists to CSV for WMS/ERP mock integration
- Optional Streamlit companion app (separate repo path / branch policy)

---

## 15. Naming Policy

User-facing labels, workbook metadata, documentation, and demo scripts must **not** contain legacy internal codenames. Migration history referencing the source branch is confined to [docs/BRANCH_SEPARATION.md](docs/BRANCH_SEPARATION.md).

---

## 16. Related Documents

- [specs.md](specs.md) — technical specification
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — module layout and data flow
- [docs/BUSINESS_RULES.md](docs/BUSINESS_RULES.md) — rule priority and thresholds
- [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) — field definitions
- [docs/CHANGELOG.md](docs/CHANGELOG.md) — release history
