# Inventory & IT Asset Control Toolkit

**Version:** v1.0.0 · **Author:** Daniel A. Cruz

A Python project that generates a professional, interview-ready Excel workbook for **inventory optimization** and **IT asset lifecycle management**. Built to demonstrate supply chain analytics, exception reporting, audit readiness, and executive visibility — all from reproducible source code.

> **Sample data disclaimer:** All records in this project are **fictional**. No real company, customer, employee, or asset information is represented. The workbook is intended for portfolio, interview, and demonstration use only.

---

## Overview

Running a single command produces `Inventory_IT_Asset_Control_Toolkit.xlsx` — a 12-tab workbook covering warehouse inventory health, transfer and markdown planning, IT asset tracking, audit reconciliation, software license compliance, mobile provisioning, disposal logging, and a printable management summary.

The toolkit separates **data generation** from **workbook assembly**, uses centralized styling and business rules, and outputs deterministic sample data (seed `42`) so demos and tests are repeatable.

**Opening statement for interviews:**

> *"I built this toolkit to demonstrate how I approach inventory and asset control: clean data capture, lifecycle tracking, exception reporting, audit readiness, and management visibility. The same disciplined process applies whether I am analyzing warehouse inventory, retail stock, IT assets, software licenses, or equipment lifecycle status."*

---

## Screenshot

<!-- Portfolio tip: capture the Inventory Dashboard or Management Summary tab after build and add the image here. -->

*Screenshot placeholder — run `./build.sh` and add a workbook screenshot for GitHub portfolio display.*

---

## Features

- **Modular architecture** — generators, sheet builders, styling, and formulas in separate layers
- **Deterministic fictional data** — seeded generators with curated interview scenarios (aged stock, over-assigned licenses, missing assets, pending wipe, etc.)
- **Professional Excel output** — navy headers, KPI cards, filterable tables, conditional formatting, charts, and dropdown validations
- **Cross-sheet formulas** — dashboard and management summary KPIs reference operational tabs
- **Two demo paths** — Inventory Optimization (Mavis-style) and IT Inventory Control in one workbook
- **Automated build & tests** — one command to generate CSVs and workbook; pytest coverage for data quality and workbook integrity
- **No macros or manual cleanup** — entire workbook generated with `openpyxl`

---

## Workbook Tabs

| # | Tab | Purpose |
|---|-----|---------|
| 1 | README | Toolkit guide, demo paths, and interview talking points |
| 2 | Master Inventory | Operational inventory dataset with status and recommended actions |
| 3 | Inventory Dashboard | Leadership KPIs, summary tables, and charts |
| 4 | Aged Excess Analysis | Slow-moving, aged, excess, and obsolete inventory exceptions |
| 5 | Markdown Planner | Markdown rules, disposition modeling, and margin protection |
| 6 | Transfer Planner | Category-level transfer recommendations between locations |
| 7 | IT Asset Register | Full IT asset lifecycle register |
| 8 | Audit Reconciliation | System vs. physical audit samples and exception tracking |
| 9 | Software Licenses | License compliance, renewals, and annual cost summary |
| 10 | Mobile Provisioning | Device issuance, MDM checklist, and recovery status |
| 11 | Disposal Log | Asset retirement, data wipe, and certificate tracking |
| 12 | Management Summary | Printable one-page executive overview |

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Language | Python 3.11+ |
| Excel generation | [openpyxl](https://openpyxl.readthedocs.io/) |
| Data & analysis | pandas, numpy |
| Fictional sample data | Faker |
| Date handling | python-dateutil |
| Testing | pytest |
| Code quality | black, ruff |

---

## Installation

Clone the repository and install dependencies from the project root:

```bash
cd inventory-it-asset-toolkit
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## How to Run

From the project root (`inventory-it-asset-toolkit/`):

```bash
python src/main.py
```

**One-command build scripts** (recommended — each script changes to the project directory first, then runs the build):

| Platform | Command |
|----------|---------|
| macOS / Linux | `./build.sh` |
| Windows | `build.bat` |

On macOS/Linux, make the script executable once if needed: `chmod +x build.sh`

The scripts only run `python src/main.py` — no destructive operations, no external downloads, no git commands.

The build process will:

1. Create `dist/` and `data/generated/` if missing
2. Generate all fictional sample datasets
3. Save CSV files to `data/generated/`
4. Build the Excel workbook
5. Print a success message with the output path

---

## Output Location

| Output | Path |
|--------|------|
| **Workbook** | `dist/Inventory_IT_Asset_Control_Toolkit.xlsx` |
| **Generated CSVs** | `data/generated/*.csv` |

Re-running the build **overwrites** generated outputs only. Source code is never modified.

---

## Interview Demo Paths

### Inventory Optimization (Mavis-style) · ~3 minutes

**Recommended tab order:**

1. **Inventory Dashboard** — total value, aged/excess inventory, transfer and markdown candidates, recovery value
2. **Aged Excess Analysis** — drill into slow-moving and obsolete SKUs by location
3. **Transfer Planner** — evaluate moving excess before markdown
4. **Markdown Planner** — model disposition while protecting margin
5. **Management Summary** — close with executive KPIs and 30/60/90-day plan

**Suggested narrative:**

> *"This section focuses on inventory optimization. The dashboard shows inventory value, aged stock, excess inventory, transfer candidates, markdown candidates, and estimated recovery value. From there, I drill into aged and excess inventory, evaluate whether a transfer should happen before markdown, and use the markdown planner to protect margin while exiting slow-moving inventory."*

---

### IT Inventory Control · ~3 minutes

**Recommended tab order:**

1. **IT Asset Register** — lifecycle tracking from receipt through assignment and retirement
2. **Audit Reconciliation** — system vs. physical audit exceptions and follow-up owners
3. **Software Licenses** — over-assigned licenses, renewal risk, and annual cost
4. **Mobile Provisioning** — MDM checklist, pending setup, and user agreement gaps
5. **Disposal Log** — data wipe, vendor disposal, and certificate status
6. **Management Summary** — tie IT control metrics into a leadership one-pager

**Suggested narrative:**

> *"This section focuses on IT asset lifecycle control. The asset register tracks equipment from receipt through assignment, audit, return, repair, data wipe, and disposal. Audit reconciliation compares system inventory against physical audit results and flags exceptions. The license tracker and mobile provisioning tabs help standardize compliance and equipment control."*

---

## Running Tests

```bash
pytest src/tests/
```

Tests verify data generation, required columns, business-rule scenarios (e.g., over-assigned licenses), workbook creation, sheet order, and openpyxl readability.

---

## Project Structure

```text
inventory-it-asset-toolkit/
├── build.sh             # One-command build (macOS / Linux)
├── build.bat            # One-command build (Windows)
├── config/              # Workbook paths, thresholds, styling constants
├── data/generated/      # Generated CSV sample data
├── dist/                # Output .xlsx workbook
├── docs/                # Architecture and demo script
├── src/
│   ├── main.py          # Build entry point
│   ├── data_generation/ # Fictional dataset generators
│   ├── workbook/        # Builder, styles, formulas, charts, validations
│   ├── sheets/          # One module per worksheet
│   └── tests/           # pytest suite
├── PRD.md               # Product requirements
├── specs.md             # Technical specifications
└── requirements.txt
```

---

## Future Enhancements

- Power BI or Streamlit dashboard layer on top of generated CSVs
- ERP / CMDB import-export templates (SAP, Oracle, ServiceNow-style)
- Scheduled refresh and email distribution of management summary
- Additional scenario packs for retail, healthcare, or field-service demos
- Web app or AI assistant for natural-language inventory and asset queries

---

## License

Portfolio and demonstration use. All data is fictional.
