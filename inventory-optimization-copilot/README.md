# Inventory Optimization Copilot

**Version:** v2.0.0 · **Author:** Daniel A. Cruz · **Branch:** `feature/inventory-optimization-copilot`

Python project that generates a professional, interview-ready Excel workbook for **inventory optimization** — ABC classification, cycle counting, replenishment, forecasting, service levels, purchase orders, vendor scorecards, network transfers, markdown modeling, and executive reporting.

> **Disclaimer:** All sample data is **fictional** and intended for portfolio and interview demonstrations only. It does not represent any real company, customer, or ERP system.

**Copilot** means structured decision support (recommendations, prioritization, and management guidance) embedded in the workbook — **not** a live AI model or chat interface.

---

## Quick Start

```bash
cd inventory-optimization-copilot
pip install -r requirements.txt
./build.sh          # macOS / Linux  (or: build.bat on Windows)
```

**Output:** `dist/Inventory_Optimization_Copilot.xlsx`

Or run directly:

```bash
python src/main.py
```

---

## Features (v2.0.0)

| Capability | Description |
|------------|-------------|
| Master inventory dataset | 22-field operational table with derived status and actions |
| ABC classification & cycle counts | Turnover, DOH, accuracy, and risk-based count plans |
| Replenishment planning | Safety stock, ROP, EOQ, and order recommendations |
| Demand forecast | Statistical methods with WAPE-based selection |
| Service level analysis | Fill rates, backorders, and gap diagnostics |
| Purchase order tracker | Open supply, lateness, and receipt status |
| Vendor scorecards | OTIF, quality, lead time, and risk classification |
| Network transfer planner | Deterministic surplus allocation with net-benefit economics |
| Markdown planner | Transfer-first dispositions with recovery modeling |
| Executive dashboard | 27 KPIs across four sections and 10 charts |
| Management summary | Printable two-page inventory executive overview |

**Deterministic build:** `RANDOM_SEED=42`, `AS_OF_DATE=2026-07-01`

---

## Workbook Tabs (14)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | README | Product guide, navigation, and demo path |
| 2 | Master Inventory | Operational inventory dataset |
| 3 | Inventory Dashboard | Leadership KPIs and charts |
| 4 | Inventory Classification | ABC, turnover, DOH, and accuracy |
| 5 | Aged Excess Analysis | Exception inventory queue |
| 6 | Cycle Count Plan | Risk-based count schedule |
| 7 | Replenishment Planning | Safety stock, ROP, and orders |
| 8 | Transfer Planner | Network transfer recommendations |
| 9 | Markdown Planner | Markdown and disposition modeling |
| 10 | Demand Forecast | Statistical demand projections |
| 11 | Service Level Analysis | Fill rates and service gaps |
| 12 | Purchase Order Tracker | Open PO monitoring |
| 13 | Vendor Scorecards | Supplier performance and risk |
| 14 | Management Summary | Printable executive overview |

---

## Datasets (8 CSV files)

Generated under `data/generated/` on each build:

| File | Description |
|------|-------------|
| `inventory_data.csv` | Master inventory (~120 rows) |
| `inventory_snapshots.csv` | Weekly snapshot history |
| `demand_history.csv` | Weekly demand by SKU-location |
| `customer_orders.csv` | Order lines for fill-rate analytics |
| `cycle_counts.csv` | Count history and accuracy |
| `suppliers.csv` | Fictional supplier master |
| `purchase_orders.csv` | Open and historical PO lines |
| `purchase_order_receipts.csv` | Receipt events |

Categories: tires, brake parts, batteries, filters, fluids, tools, shop supplies, accessories. Locations: 3 distribution centers + 8 retail stores (Northeast / NYC Metro).

---

## Architecture Summary

Business logic lives in **`src/services/`**; sheet modules in **`src/sheets/`** handle layout and styling only.

```text
src/main.py → data_generation → services (metrics, KPIs, planners) → sheets → workbook/builder.py
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for module layout and extension points.

---

## Install

**Requirements:** Python 3.11+

```bash
pip install -r requirements.txt
```

---

## Build & Quality Commands

| Task | Command |
|------|---------|
| Build workbook | `python src/main.py` |
| Tests | `pytest -q` |
| Full quality gate | See below |

```bash
python -m compileall src config
ruff check .
black --check .
mypy src config
pytest --cov=src/services --cov=src/domain/validation --cov-report=term-missing --cov-fail-under=85 -q
python src/main.py
```

CI runs the same gate via `.github/workflows/ci.yml` (no auto-merge or deploy).

---

## Demo Path (~10 min)

1. **README** — product framing  
2. **Inventory Dashboard** — KPIs and charts  
3. **Inventory Classification** — ABC and accuracy  
4. **Aged Excess Analysis** — exception queue  
5. **Replenishment Planning** — order recommendations  
6. **Transfer Planner** — network optimization  
7. **Markdown Planner** — recovery modeling  
8. **Demand Forecast & Service Level** — planning accuracy  
9. **Purchase Order Tracker & Vendor Scorecards** — supply risk  
10. **Management Summary** — executive close  

Full script: [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)

---

## Limitations

- Fictional data only; no ERP or WMS integration
- Recommendations computed at build time, not interactively
- Transfer costs use lane-based estimates; markdown sell-through uses modeled uplift
- Excel formulas on dashboard/summary are supplementary; Python is generation source of truth
- Separate product branch excludes enterprise asset-control capabilities (see [docs/BRANCH_SEPARATION.md](docs/BRANCH_SEPARATION.md))

---

## Branch

This product lives on:

```text
feature/inventory-optimization-copilot
```

Historical baselines (`main`, source inventory branch) are preserved unchanged per separation policy.

---

## Documentation

| Document | Description |
|----------|-------------|
| [prd.md](prd.md) | Product requirements (14-sheet contract) |
| [specs.md](specs.md) | Technical specification |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Module layout and data flow |
| [docs/BUSINESS_RULES.md](docs/BUSINESS_RULES.md) | Rule priority and thresholds |
| [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) | Fields and metrics |
| [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) | Interview walkthrough |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Release history |
| [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) | Pre-release verification |
| [docs/BRANCH_SEPARATION.md](docs/BRANCH_SEPARATION.md) | Branch split and scope |

---

## License

Portfolio / demonstration project. See repository root for license terms if applicable.
