# Demo Script — Inventory Optimization Copilot

**Product:** Inventory Optimization Copilot v2.0.0  
**Workbook:** `dist/Inventory_Optimization_Copilot.xlsx`  
**Audience:** Supply chain, procurement, warehouse, and executive stakeholders

## Setup (before the demo)

```bash
cd inventory-optimization-copilot
pip install -r requirements.txt
python src/main.py
```

Open `dist/Inventory_Optimization_Copilot.xlsx`.

## Demo Path (~8 minutes)

### 1. README (~1 min)

- Explain fictional, seed-42 sample data and as-of date `2026-07-01`.
- Walk through the tab order and decision-support purpose (not a live AI model).

### 2. Master Inventory (~1.5 min)

- Show item-level fields: on-hand, demand, age, status, recommended action.
- Highlight mix of healthy, excess, slow-moving, and obsolete SKUs.

### 3. Inventory Dashboard (~1.5 min)

- Review KPI tiles: total units, inventory value, aged/excess exposure.
- Point to charts for status mix and top risk categories.

### 4. Aged Excess Analysis (~1 min)

- Filter to exception inventory (aged, excess, obsolete).
- Discuss operational follow-up: transfer vs markdown vs liquidate.

### 5. Transfer Planner (~1 min)

- Show SKUs where network transfer is recommended before markdown.
- Explain destination demand buffer logic.

### 6. Markdown Planner (~1 min)

- Review recommended markdown % and disposition by age band.
- Tie margin impact to recovery vs holding cost narrative.

### 7. Management Summary (~1 min)

- Printable one-page executive view: exposure, actions, and priorities.
- Close with reproducible build (`python src/main.py`) for interview credibility.

## Talking Points

| Stakeholder | Lead with |
|-------------|-----------|
| Inventory / supply chain analyst | Master Inventory → Aged Excess |
| Procurement / vendor manager | Dashboard exposure → future PO/Vendor tabs |
| Executive / GM | Management Summary → Dashboard KPIs |

## Out of Scope for This Product

IT asset register, software licenses, mobile provisioning, audit reconciliation, and disposal log belong to the separate **IT Asset Control Toolkit** product (future branch).
