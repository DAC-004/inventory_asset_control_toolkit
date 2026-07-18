# Demo Script — Inventory Optimization Copilot v2.0.0

**Duration:** ~10 minutes  
**Audience:** Hiring manager, supply chain leader, or analytics stakeholder  
**Artifact:** `dist/Inventory_Optimization_Copilot.xlsx`  
**Branch:** `feature/inventory-optimization-copilot`

---

## Before You Start

1. Build fresh output:

   ```bash
   cd inventory-optimization-copilot
   pip install -r requirements.txt
   python src/main.py
   ```

2. Open `dist/Inventory_Optimization_Copilot.xlsx` in Excel or LibreOffice.
3. Optional: print **Management Summary** for leave-behind.
4. Remember: all data is **fictional**; Copilot = **decision support**, not live AI.

**Opening line (30 sec):**

> "I built Inventory Optimization Copilot to show how I turn raw stock data into prioritized actions — transfers before markdowns, margin-aware exit planning, and an executive view leadership can use without opening every tab."

---

## Minute 0:00–1:00 — README

**Tab:** README

**Show:**

- Product name and v2.0.0
- Fictional-data disclaimer
- Tab list and suggested demo order

**Say:**

- Python generates the entire workbook deterministically (seed 42, as-of 2026-07-01).
- Business rules live in services; sheets are presentation.
- v2.0.0 delivers all 14 inventory planning tabs with deterministic build (seed 42, as-of 2026-07-01).

---

## Minute 1:00–3:00 — Master Inventory

**Tab:** Master Inventory

**Show:**

- Header row and frozen panes
- Key columns: Location, Quantity On Hand, Min/Max Stock, Age Days, 90 Day Demand, Status, Recommended Action
- Filter Status → show each label exists (Healthy through Obsolete)

**Say:**

- Total value = qty × unit cost; margin and sell-through computed in Python.
- Status rules are priority-ordered: stockout first, then obsolete, excess/aged, excess, slow-moving, else healthy.
- This single dataset feeds dashboard, exception reports, and both planners.

**Optional deep dive:** One **Excess / Aged** row — qty above max with age > 180 days → action "Transfer or Markdown."

---

## Minute 3:00–5:00 — Inventory Dashboard

**Tab:** Inventory Dashboard

**Show:**

- KPI card row (10 metrics)
- Charts: value by location, status breakdown, aging buckets, action summary, top excess

**Say:**

- Leadership sees dollars at risk (aged, excess) and counts (slow-moving, obsolete, stockout).
- Transfer and markdown candidate counts tie directly to recommended actions on Master Inventory.
- Estimated recovery value aggregates inventory exposed to markdown/liquidation paths.
- KPI cards use Excel formulas referencing Master Inventory for transparency.

**Pivot if short on time:** Skip aging chart; keep KPI row + status breakdown.

---

## Minute 5:00–6:30 — Aged Excess Analysis

**Tab:** Aged Excess Analysis

**Show:**

- Sorted by risk (High first) then inventory value
- Risk Level, Issue Type, Analyst Notes columns
- One High row (Obsolete or Excess / Aged) and one Medium row

**Say:**

- This is the analyst's exception queue — only non-low-risk rows.
- Analyst notes encode standard playbooks (replenish, transfer before markdown, liquidation review).
- Excess quantity is explicit: max(qty − max stock, 0).

---

## Minute 6:30–8:30 — Transfer Planner

**Tab:** Transfer Planner

**Show:**

- Source vs. destination locations
- Suggested Transfer Quantity, Transfer Cost, Net Benefit
- Rows with "Transfer Recommended" vs. "Review Transfer"

**Say:**

- Logic prefers moving stock across the network before discounting.
- Source must have excess; destination must be below min or show strong demand.
- Net benefit = margin protected minus lane-based transfer cost — negative rows excluded entirely.
- Same-SKU and same-category substitution lanes are both considered.

**Highlight:** Top row by Net Benefit — walk through economics in one sentence.

---

## Minute 8:30–9:30 — Markdown Planner

**Tab:** Markdown Planner

**Show:**

- Suggested Markdown %, Markdown Price, Projected Sell Through, Estimated Recovery Value, Margin Impact
- Disposition column: Hold, Transfer First, 10%/20% Markdown, Liquidate

**Say:**

- Only eligible statuses appear (slow-moving, excess variants, obsolete).
- Age bands drive markdown depth; pure excess may show "Transfer First" at 0% markdown.
- Recovery and margin impact quantify the cost of clearance vs. holding.

---

## Minute 9:30–10:00 — Management Summary

**Tab:** Management Summary

**Show:**

- KPI strip (5 metrics)
- Top 5 inventory risks table
- Recommended action counts
- 30/60/90-day action placeholders

**Say:**

- Printable one-pager for stand-ups or exec email.
- Top risks pulled from the same aged/excess logic — no duplicate rule sets.
- Roadmap adds classification, replenishment, forecast, PO/vendor views without changing this narrative.

**Closing line:**

> "The same pattern I'd use in production: centralized rules, reproducible data, Excel as the delivery layer stakeholders already use."

---

## Anticipated Questions

| Question | Answer |
|----------|--------|
| Is this connected to our ERP? | No — fictional CSV input; designed to mirror ERP export shapes. |
| Is Copilot an AI chatbot? | No — pre-computed recommendations at build time. |
| Can we change thresholds? | Yes — `config/workbook_config.py`, then rebuild. |
| Why Excel? | Interview portability; stakeholders can filter and share without a app login. |
| What's next? | Seven sheets in prompts 04–09: ABC, cycle count, replenishment, forecast, service level, PO, vendors. |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Workbook missing | Run `python src/main.py` from project root |
| Blank planners | Regenerate with seed 42; check Master has excess/slow rows |
| Formula errors | Open in Excel and enable automatic calculation |

---

## Related Documents

- [../prd.md](../prd.md) — full requirements
- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) — pre-demo verification
