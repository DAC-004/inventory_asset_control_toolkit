# Architecture — Inventory Optimization Copilot v2.0.0

Production architecture for the Python + openpyxl workbook generator. Business logic lives in **services**; sheet modules handle layout, styling, and I/O only.

---

## 1. System Overview

```text
┌─────────────────────────────────────────────────────────────────┐
│                        src/main.py                              │
│  ensure dirs → generate data → build_workbook → verify output   │
└────────────┬───────────────────────────────┬────────────────────┘
             │                               │
             ▼                               ▼
┌────────────────────────┐      ┌────────────────────────────────┐
│  data_generation/      │      │  workbook/builder.py           │
│  generate_inventory.py │      │  SHEET_ORDER → SHEET_BUILDERS  │
└────────────┬───────────┘      └───────────────┬────────────────┘
             │                                    │
             │         ┌──────────────────────────┼──────────────────┐
             │         ▼                          ▼                  ▼
             │   src/services/*            src/sheets/*        workbook/*
             │   (business logic)          (presentation)      (styles, formulas)
             ▼
      data/generated/inventory_data.csv
      dist/Inventory_Optimization_Copilot.xlsx
```

**Determinism:** `RANDOM_SEED=42`, `AS_OF_DATE=2026-07-01` in `config/workbook_config.py`.

**Copilot semantics:** Recommendations are pre-computed at build time. No runtime AI, no external services.

---

## 2. Module Layout

```text
inventory-optimization-copilot/
├── config/
│   ├── workbook_config.py    # Paths, version, thresholds, SHEET_ORDER
│   └── style_config.py       # Colors, fonts, number formats
├── src/
│   ├── main.py               # CLI entry point
│   ├── domain/
│   │   ├── constants.py      # Shared labels, buckets, column refs
│   │   └── schemas.py        # INVENTORY_COLUMN_ORDER
│   ├── data_generation/
│   │   └── generate_inventory.py
│   ├── services/             # ★ Business logic (source of truth)
│   │   ├── inventory_metrics.py
│   │   ├── inventory_health_service.py
│   │   ├── kpi_service.py
│   │   ├── kpi_dashboard_service.py
│   │   ├── markdown_service.py
│   │   ├── transfer_service.py
│   │   └── summary_service.py
│   ├── sheets/               # Presentation only
│   │   ├── readme_sheet.py
│   │   ├── master_inventory_sheet.py
│   │   ├── inventory_dashboard_sheet.py
│   │   ├── aged_excess_sheet.py
│   │   ├── markdown_planner_sheet.py
│   │   ├── transfer_planner_sheet.py
│   │   └── management_summary_sheet.py
│   ├── workbook/
│   │   ├── builder.py        # Orchestration
│   │   ├── styles.py
│   │   ├── formulas.py
│   │   ├── charts.py
│   │   ├── validations.py
│   │   └── utils.py
│   └── tests/
├── data/generated/
├── dist/
└── docs/
```

---

## 3. Layer Responsibilities

| Layer | Responsibility | Must NOT |
|-------|----------------|----------|
| `domain/` | Constants, column order, shared enums | Contain I/O or openpyxl calls |
| `data_generation/` | Fictional CSV/DataFrame creation | Embed sheet layout logic |
| `services/` | Metrics, status rules, aggregations, planner DataFrames | Import openpyxl |
| `sheets/` | Write cells, apply styles, insert charts | Duplicate business rules |
| `workbook/` | Cross-cutting Excel utilities, builder orchestration | Assign inventory status |
| `config/` | Thresholds, paths, sheet order | Business branching beyond constants |

---

## 4. Data Flow

### 4.1 Build pipeline

1. **`main.py`** creates `dist/` and `data/generated/`.
2. **`generate_inventory_data()`** builds a DataFrame with derived fields via `inventory_metrics`.
3. **`save_inventory_data()`** writes `inventory_data.csv`.
4. **`build_workbook({"inventory": df})`** iterates `SHEET_ORDER`.
5. Each **sheet builder** receives `(worksheet, context)` where `context = {"data": datasets, "workbook": wb}`.
6. Sheet builders call **services** to obtain computed DataFrames or KPI definitions, then render.

### 4.2 Service consumption map (Phase 1)

| Sheet | Primary services |
|-------|------------------|
| Master Inventory | `inventory_metrics` (during generation) |
| Inventory Dashboard | `kpi_service`, `kpi_dashboard_service` |
| Aged Excess Analysis | `inventory_health_service` |
| Markdown Planner | `markdown_service` |
| Transfer Planner | `transfer_service` |
| Management Summary | `summary_service`, `kpi_service` |

### 4.3 Formula vs. Python policy

- **Python:** Status, actions, planner rows, chart source tables, data generation.
- **Excel formulas:** Dashboard and Management Summary KPI cards reference Master Inventory ranges for transparency (`kpi_service`).
- **Tests:** Assert Python outputs; optionally spot-check formula strings.

---

## 5. Workbook Builder

`src/workbook/builder.py`:

```python
SHEET_BUILDERS = {
    "README": readme_sheet.build,
    "Master Inventory": master_inventory_sheet.build,
    # ...
}
```

Extension pattern for prompts 04–09:

1. Add service module(s) under `src/services/`.
2. Add sheet builder under `src/sheets/`.
3. Register in `SHEET_BUILDERS`.
4. Insert name in `SHEET_ORDER` (`config/workbook_config.py`).
5. Add tests mirroring existing sheet test modules.

---

## 6. Configuration

**Single source of truth:** `config/workbook_config.py`

| Constant group | Examples |
|----------------|----------|
| Identity | `WORKBOOK_TITLE`, `VERSION`, `OUTPUT_FILENAME` |
| Determinism | `RANDOM_SEED`, `AS_OF_DATE` |
| Structure | `SHEET_ORDER`, `ROW_COUNTS` |
| Rules | `INVENTORY_THRESHOLDS`, `MARKDOWN_THRESHOLDS`, `TRANSFER_SETTINGS` |

Visual tokens live in `config/style_config.py`. Sheet builders import both.

---

## 7. Domain Model

**Inventory record:** 22 columns per `src/domain/schemas.py` (`INVENTORY_COLUMN_ORDER`).

Shared presentation constants (`AGING_BUCKETS`, `ANALYST_NOTES`, Master sheet column letters) live in `src/domain/constants.py` to avoid circular imports between services and workbook layers.

---

## 8. Extension Points

### Adding a planned sheet (example: Replenishment Planning)

1. **`replenishment_service.py`** — compute safety stock, ROP, EOQ, projected availability.
2. **`replenishment_planning_sheet.py`** — render table + optional KPI strip.
3. **Data** — extend generator or add `generate_purchase_orders.py` if PO data required.
4. **Tests** — `test_replenishment_service.py`, `test_replenishment_planning_sheet.py`.
5. **Docs** — update PRD status, CHANGELOG, DATA_DICTIONARY.

### Adding a metric

1. Implement in appropriate `services/` module.
2. Expose via existing aggregation or new service function.
3. Wire into sheet builder (display only).
4. Document in `docs/DATA_DICTIONARY.md` and `docs/BUSINESS_RULES.md` if rule-driven.

---

## 9. Testing Architecture

```text
src/tests/
├── test_data_generation.py      # Seed, columns, status coverage
├── test_workbook_build.py       # End-to-end build
├── test_required_sheets.py      # Tab order and presence
├── test_*_sheet.py              # Per-sheet smoke + content
├── test_requirements.py         # Product identity guards
└── test_spec_requirements.py    # Spec compliance
```

**CI:** `.github/workflows/ci.yml` runs compile, ruff, black, mypy, pytest, and build.

---

## 10. Dependencies

| Package | Role |
|---------|------|
| openpyxl | Workbook creation |
| pandas | DataFrames, groupby |
| numpy | Numeric generation |
| faker | Realistic text (controlled by seed) |
| pytest / ruff / black / mypy | Quality gate |

No database, web server, or cloud SDK.

---

## 11. Security & Portability

- All data fictional; no PII.
- No network calls at build time.
- Output is a standalone `.xlsx` suitable for email or USB demo.

---

## 12. Related Documents

- [BUSINESS_RULES.md](BUSINESS_RULES.md)
- [DATA_DICTIONARY.md](DATA_DICTIONARY.md)
- [BRANCH_SEPARATION.md](BRANCH_SEPARATION.md)
- [../specs.md](../specs.md)
