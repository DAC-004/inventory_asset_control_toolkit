# Requirements Checklist

Comparison of **PRD.md**, **specs.md**, and **prompts.md** against the current implementation.

**Status:** Complete — workbook builds successfully with all 12 required sheets.

Last verified: run `python src/main.py` and `pytest src/tests/ -q`

---

## Project Scaffold & Config

| Requirement | Status |
|-------------|--------|
| Python 3.11+ project structure | ✅ Complete |
| `config/workbook_config.py` (paths, sheet order, thresholds) | ✅ Complete |
| `config/style_config.py` (colors, fonts, formats) | ✅ Complete |
| `requirements.txt` with openpyxl, pandas, numpy, faker, pytest | ✅ Complete |
| `.gitignore` for generated outputs | ✅ Complete |

---

## Data Generation

| Requirement | Status |
|-------------|--------|
| Inventory generator (22 columns, business rules, all statuses) | ✅ Complete |
| IT asset generator (16 columns, lifecycle scenarios) | ✅ Complete |
| Software generator (compliance rules, renewals 30/60/90 days) | ✅ Complete |
| Mobile generator (all statuses, curated scenarios) | ✅ Complete |
| Disposal generator (disposal rules, curated scenarios) | ✅ Complete |
| CSV export to `data/generated/` | ✅ Complete |
| Fictional data only (seed 42) | ✅ Complete |
| Inventory 80–150 rows (default 120) | ✅ Complete |
| IT assets 80–150 rows (default 120) | ✅ Complete |
| Software 15–30 rows (default 22) | ✅ Complete |
| Multiple DCs (3) and stores (8+) | ✅ Complete |
| Device types: laptops, desktops, printers, scanners, phones, monitors, network | ✅ Complete |

---

## Workbook Infrastructure

| Requirement | Status |
|-------------|--------|
| `workbook/builder.py` orchestration | ✅ Complete |
| `workbook/styles.py` reusable styling | ✅ Complete |
| `workbook/formulas.py` cross-sheet formulas | ✅ Complete |
| `workbook/charts.py` bar and pie charts | ✅ Complete |
| `workbook/utils.py` tables, formats, print layout | ✅ Complete |
| `workbook/validations.py` dropdown lists | ✅ Complete |
| Output: `dist/Inventory_IT_Asset_Control_Toolkit.xlsx` | ✅ Complete |
| No macros / VBA | ✅ Complete |

---

## Worksheet Tabs (12 required)

| Sheet | Status |
|-------|--------|
| README | ✅ Complete |
| Master Inventory | ✅ Complete |
| Inventory Dashboard | ✅ Complete |
| Aged Excess Analysis | ✅ Complete |
| Markdown Planner | ✅ Complete |
| Transfer Planner | ✅ Complete |
| IT Asset Register | ✅ Complete |
| Audit Reconciliation | ✅ Complete |
| Software Licenses | ✅ Complete |
| Mobile Provisioning | ✅ Complete |
| Disposal Log | ✅ Complete |
| Management Summary | ✅ Complete |

Sheet order matches `SHEET_ORDER` in config.

---

## Sheet Features

| Requirement | Status |
|-------------|--------|
| README: title, version, author, disclaimer, demo paths, navigation | ✅ Complete |
| Master Inventory: table, CF, dropdowns, formats, filters | ✅ Complete |
| Dashboard: 10 KPIs, 5 summary tables, 4 charts | ✅ Complete |
| Aged Excess: derived fields, risk CF, filters | ✅ Complete |
| Markdown Planner: rules, disposition CF, formats | ✅ Complete |
| Transfer Planner: category matching, net benefit CF | ✅ Complete |
| IT Asset Register: lifecycle CF, warranty watch, dropdowns | ✅ Complete |
| Audit Reconciliation: KPIs, system/physical samples, exceptions | ✅ Complete |
| Software Licenses: summary KPIs, compliance CF, validations | ✅ Complete |
| Mobile Provisioning: checklist summary, status CF, validations | ✅ Complete |
| Disposal Log: pipeline summary, status CF, validations | ✅ Complete |
| Management Summary: inventory/IT/software/disposal sections, top risks, action plan | ✅ Complete |

---

## Design & Excel Features

| Requirement | Status |
|-------------|--------|
| Navy header theme (`#1F4E78`) | ✅ Complete |
| KPI cards (light blue fill) | ✅ Complete |
| Conditional formatting for risks | ✅ Complete |
| Filterable Excel tables | ✅ Complete |
| Frozen header rows (operational sheets) | ✅ Complete |
| Currency / percentage / date / integer formats | ✅ Complete |
| Autosized columns | ✅ Complete |
| Hidden gridlines on data sheets | ✅ Complete |
| Print-ready Management Summary (landscape, fit to page) | ✅ Complete |

---

## Business Rules

| Rule set | Status |
|----------|--------|
| Inventory status (§7.1) | ✅ Complete |
| Markdown rules (§7.2) | ✅ Complete |
| Transfer rules (§7.3) | ✅ Complete |
| Software compliance (§7.4) | ✅ Complete |
| Disposal status (§7.5) | ✅ Complete |

---

## Build, Tests & Docs

| Requirement | Status |
|-------------|--------|
| `python src/main.py` one-command build | ✅ Complete |
| `build.sh` / `build.bat` wrappers | ✅ Complete |
| Error handling and console messages | ✅ Complete |
| pytest: data, workbook, requirements, sheet tests | ✅ Complete (67+ tests) |
| README.md (overview, install, run, demos) | ✅ Complete |
| README screenshot placeholder | ✅ Complete |
| `docs/demo_script.md` | ✅ Complete |
| `docs/architecture.md` | ✅ Complete |

---

## Known Design Trade-offs

| Item | Notes |
|------|-------|
| Management Summary charts (specs §10) | Spec lists pie/bar charts for action/audit/compliance summaries; implemented as **compact summary tables** to preserve one-page print layout. Full charts live on **Inventory Dashboard**. |
| Transfer Planner SKU matching | SKUs exist at one location each; transfers use **category-level matching** (documented in architecture). |
| Recommended Actions (PRD §7.12) | Covered via inventory KPI cards + **Recommended Action Summary** table on Management Summary. |

---

## Out of Scope (by design)

Live ERP integration, macros, real company data, cloud deployment, barcode scanning, authentication — per PRD §12.

---

## Verification Commands

```bash
cd inventory-it-asset-toolkit
python src/main.py
pytest src/tests/ -q
```

Expected: workbook at `dist/Inventory_IT_Asset_Control_Toolkit.xlsx`, all tests passing.
