# Inventory & IT Asset Control Toolkit

**Version:** v1.0.0

A Python project that generates a professional Excel workbook for inventory optimization and IT asset lifecycle management. Built for interview demos and portfolio use — all sample data is fictional.

## Overview

This toolkit produces `Inventory_IT_Asset_Control_Toolkit.xlsx`, a 12-tab workbook covering:

- Warehouse inventory health, aged/excess analysis, transfer planning, and markdown modeling
- IT asset tracking, audit reconciliation, software licenses, mobile provisioning, and disposal

The workbook is generated entirely from source code using `openpyxl` — no macros, no manual Excel editing.

## Screenshot

<!-- TODO: Add screenshot of Inventory Dashboard tab -->
*Screenshot placeholder — add after dashboard implementation.*

## Features

- Modular architecture: data generation separate from workbook assembly
- Centralized styling and business rules
- Deterministic fictional sample data (seeded)
- Filterable tables, KPI sections, charts, and conditional formatting (planned)
- Two interview demo paths: Inventory Optimization and IT Inventory Control

## Workbook Tabs

1. README
2. Master Inventory
3. Inventory Dashboard
4. Aged Excess Analysis
5. Markdown Planner
6. Transfer Planner
7. IT Asset Register
8. Audit Reconciliation
9. Software Licenses
10. Mobile Provisioning
11. Disposal Log
12. Management Summary

## Requirements

- Python 3.11+
- See `requirements.txt` for dependencies

## Installation

```bash
cd inventory-it-asset-toolkit
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## How to Run

From the project root:

```bash
python src/main.py
```

Output:

```text
dist/Inventory_IT_Asset_Control_Toolkit.xlsx
data/generated/*.csv
```

## How to Regenerate Data

Re-running `python src/main.py` overwrites generated CSVs and the workbook in `dist/`. Source files are never modified.

## Interview Demo Paths

### Inventory Optimization (Mavis)

1. Inventory Dashboard
2. Aged Excess Analysis
3. Transfer Planner
4. Markdown Planner
5. Management Summary

### IT Inventory Control

1. IT Asset Register
2. Audit Reconciliation
3. Software Licenses
4. Mobile Provisioning
5. Disposal Log
6. Management Summary

## Running Tests

```bash
pytest src/tests/
```

## Project Structure

```text
inventory-it-asset-toolkit/
├── config/           # Workbook paths, version, styling constants
├── data/generated/   # Generated CSV sample data
├── dist/             # Output .xlsx workbook
├── src/
│   ├── main.py       # Build entry point
│   ├── data_generation/
│   ├── workbook/
│   ├── sheets/
│   └── tests/
├── PRD.md
└── specs.md
```

## Future Enhancements

- Full sample data generation with Faker
- Dashboard KPIs, charts, and conditional formatting
- Power BI / Streamlit dashboard versions
- ERP import/export templates

## Author

Daniel A. Cruz

## License

Portfolio / demonstration use. All data is fictional.
