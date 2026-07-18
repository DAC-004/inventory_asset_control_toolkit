# Release Checklist — Inventory Optimization Copilot v2.0.0

Pre-release verification for v2.0.0 builds. Run from `inventory-optimization-copilot/`.

---

## 1. Identity & Branch

- [ ] Branch is `feature/inventory-optimization-copilot`
- [ ] Version in `config/workbook_config.py` is `v2.0.0`
- [ ] Output filename is `Inventory_Optimization_Copilot.xlsx`
- [ ] User-facing strings contain no legacy internal codenames (see `docs/BRANCH_SEPARATION.md` for migration exception)
- [ ] Workbook metadata title = "Inventory Optimization Copilot"

---

## 2. Environment

- [ ] Python 3.11+ available
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Dev tools available for full gate: `pytest`, `ruff`, `black`, `mypy`

---

## 3. Static Quality

```bash
python -m compileall src config
ruff check .
black --check .
mypy src config
```

- [ ] All commands exit 0

---

## 4. Tests

```bash
pytest --cov=src --cov-report=term-missing -q
```

- [ ] All tests pass
- [ ] Sheet order tests pass (`test_required_sheets.py`)
- [ ] Spec/requirements guards pass (`test_requirements.py`, `test_spec_requirements.py`)
- [ ] Service and sheet unit tests pass

---

## 5. Build

```bash
python src/main.py
```

- [ ] Build completes without error
- [ ] `dist/Inventory_Optimization_Copilot.xlsx` exists
- [ ] `data/generated/inventory_data.csv` regenerated

---

## 6. Workbook Structure

Open with openpyxl or Excel:

```python
from openpyxl import load_workbook

wb = load_workbook("dist/Inventory_Optimization_Copilot.xlsx", read_only=True)
assert wb.sheetnames == [
    "README",
    "Master Inventory",
    "Inventory Dashboard",
    "Inventory Classification",
    "Aged Excess Analysis",
    "Cycle Count Plan",
    "Replenishment Planning",
    "Transfer Planner",
    "Markdown Planner",
    "Demand Forecast",
    "Service Level Analysis",
    "Purchase Order Tracker",
    "Vendor Scorecards",
    "Management Summary",
]
wb.close()
```

- [ ] Exactly **7** tabs in order above
- [ ] No out-of-product tabs present
- [ ] Tab names ≤ 31 characters

---

## 7. Content Spot Checks

### Master Inventory

- [ ] 22 columns per data dictionary
- [ ] All six statuses appear at least once (seed 42)
- [ ] All six recommended actions appear at least once

### Inventory Dashboard

- [ ] 10 KPI cards present
- [ ] 5 chart sections render

### Aged Excess Analysis

- [ ] No rows with Risk Level = Low
- [ ] Sorted High → Medium by risk

### Transfer Planner

- [ ] All rows have Net Benefit > 0
- [ ] At least one transfer recommendation (typical for seed 42)

### Markdown Planner

- [ ] Only eligible statuses listed
- [ ] Disposition values from allowed set

### Management Summary

- [ ] Inventory-only content (no non-inventory domain sections)
- [ ] Top risks table populated

---

## 8. Architecture Compliance

- [ ] Business logic in `src/services/`, not duplicated in `src/sheets/`
- [ ] Thresholds centralized in `config/workbook_config.py`
- [ ] No openpyxl imports in services modules

---

## 9. Documentation

- [ ] `README.md` reflects Phase 1 scope and doc links
- [ ] `prd.md` marks Phase 1 vs. planned sheets
- [ ] `specs.md` matches module layout (`src/services/`, not legacy paths)
- [ ] `docs/CHANGELOG.md` includes v2.0.0 entry
- [ ] `docs/DEMO_SCRIPT.md` walkthrough validated once

---

## 10. Demo Readiness

- [ ] Ran [DEMO_SCRIPT.md](DEMO_SCRIPT.md) once end-to-end (< 12 min)
- [ ] Fictional-data disclaimer stated in README and README sheet
- [ ] Copilot described as decision support, not live AI

---

## 11. CI (if pushing)

- [ ] `.github/workflows/ci.yml` green on branch
- [ ] No secrets or real PII in generated CSV/XLSX

---

## 12. Sign-off

| Role | Name | Date | Notes |
|------|------|------|-------|
| Builder | | | |
| Reviewer | | | |

---

## Quick One-Liner (full gate)

```bash
python -m compileall src config && \
ruff check . && black --check . && mypy src config && \
pytest --cov=src --cov-report=term-missing -q && \
python src/main.py
```

---

## Related Documents

- [CHANGELOG.md](CHANGELOG.md)
- [REQUIREMENTS_CHECKLIST.md](REQUIREMENTS_CHECKLIST.md)
