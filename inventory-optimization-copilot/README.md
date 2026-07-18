# Inventory Optimization Copilot

**Version:** v2.0.0 · **Author:** Daniel A. Cruz

Python project that generates a professional, interview-ready Excel workbook for **inventory optimization** — health classification, aged and excess analysis, transfer planning, markdown modeling, and executive reporting.

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

## Features (Phase 1)

| Capability | Description |
|------------|-------------|
| Master inventory dataset | 22-field operational table with derived status and actions |
| Health classification | Priority-ordered rules: stockout → obsolete → excess/aged → excess → slow-moving → healthy |
| Executive dashboard | 10 KPI cards + 5 charts |
| Aged/excess exceptions | Risk-ranked analyst queue with guidance notes |
| Transfer planner | Network moves with positive net benefit before markdown |
| Markdown planner | Age-band dispositions with recovery and margin impact |
| Management summary | Printable one-page inventory overview |

**Deterministic build:** `RANDOM_SEED=42`, `AS_OF_DATE=2026-07-01`

---

## Workbook Tabs

### Phase 1 (v2.0.0) — implemented

| # | Tab | Purpose |
|---|-----|---------|
| 1 | README | Product guide and demo path |
| 2 | Master Inventory | Operational inventory dataset |
| 3 | Inventory Dashboard | Leadership KPIs and charts |
| 4 | Aged Excess Analysis | Exception inventory |
| 5 | Markdown Planner | Markdown and disposition modeling |
| 6 | Transfer Planner | Network transfer recommendations |
| 7 | Management Summary | Printable executive overview |

### Planned (prompts 04–09)

Inventory Classification · Cycle Count Plan · Replenishment Planning · Demand Forecast · Service Level Analysis · Purchase Order Tracker · Vendor Scorecards

**Final contract:** 14 sheets (seven Phase 1 + seven planned).

---

## Datasets

| File | Description |
|------|-------------|
| `data/generated/inventory_data.csv` | Master inventory export (~120 rows, seed 42) |

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
# Optional dev tools:
pip install pytest pytest-cov black ruff mypy
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
pytest --cov=src --cov-report=term-missing -q
python src/main.py
```

---

## Demo Path (~10 min)

1. **README** — product framing  
2. **Master Inventory** — data model and classification rules  
3. **Inventory Dashboard** — KPIs and charts  
4. **Aged Excess Analysis** — exception queue  
5. **Transfer Planner** — network optimization  
6. **Markdown Planner** — recovery modeling  
7. **Management Summary** — executive close  

Full script: [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)

---

## Limitations

- Fictional data only; no ERP or WMS integration
- Phase 1 excludes replenishment, forecast, PO, and vendor analytics (planned)
- Recommendations computed at build time, not interactively
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
| [docs/REQUIREMENTS_CHECKLIST.md](docs/REQUIREMENTS_CHECKLIST.md) | Requirement traceability |

---

## License

Portfolio / demonstration project. See repository root for license terms if applicable.
