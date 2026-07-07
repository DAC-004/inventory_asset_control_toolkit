# Interview Demo Scripts

**Toolkit:** Inventory & IT Asset Control Toolkit  
**Duration:** ~3 minutes per demo  
**Workbook:** `dist/Inventory_IT_Asset_Control_Toolkit.xlsx`

> **Reminder:** All data in this workbook is fictional sample data created for demonstration and interview purposes.

---

## Demo 1: Mavis Inventory Optimization

**Role focus:** Supply chain, inventory control, warehouse operations, retail replenishment  
**Suggested timing:** ~35 seconds per tab (5 tabs)

### Opening Statement (~20 seconds)

> "I built this toolkit to show how I approach inventory optimization — not just reporting numbers, but turning inventory data into decisions. I start with a leadership view of inventory health, drill into exceptions like aged and excess stock, evaluate whether a transfer makes more sense than a markdown, and close with a summary leadership can act on. Everything you see here is generated from Python, so the logic is reproducible and easy to extend."

---

### Tabs to Show

#### 1. Inventory Dashboard (~35 seconds)

**What to say:**

> "This is my starting point for any inventory review. The KPI cards pull from the Master Inventory tab and show total inventory value, aged inventory value, excess value, transfer candidates, markdown candidates, and estimated recovery value.
>
> The summary tables and charts break that down by location, status, aging bucket, and recommended action. In a real environment, this is the view I would use in a weekly ops meeting to decide where to focus — stockout risk, slow movers, or excess at a specific DC or store."

**Point at:** KPI cards, location bar chart, status breakdown, aging bucket chart.

---

#### 2. Aged Excess Analysis (~35 seconds)

**What to say:**

> "When leadership asks 'what's actually at risk,' I move from the dashboard into the exception detail. This tab filters out healthy inventory and focuses on slow-moving, excess, aged, and obsolete items.
>
> Each row shows SKU, location, age, demand, sell-through, inventory value, risk level, and a recommended action. The conditional formatting makes high-risk items easy to spot. This is where I would prioritize analyst time — not on every SKU, but on the items driving tied-up cash."

**Point at:** Risk level column, issue type, recommended action, filterable table.

---

#### 3. Transfer Planner (~35 seconds)

**What to say:**

> "Before I markdown inventory, I ask whether it can be redeployed. The Transfer Planner matches excess inventory at one location with demand at another — at the category level, not just individual SKUs in isolation.
>
> Each recommendation shows source, destination, quantity, transfer cost, and net benefit. The idea is to recover value through redistribution first, which protects margin and avoids unnecessary write-downs. In practice, this supports conversations with logistics and store operations, not just finance."

**Point at:** Transfer recommendations, net benefit column, summary metrics.

---

#### 4. Markdown Planner (~35 seconds)

**What to say:**

> "If transfer isn't viable, I model markdown and disposition options here. Business rules drive the recommended markdown percentage and disposition — hold, 10%, 20%, or liquidate — based on age and demand signals.
>
> This tab helps answer the question: 'If we need to exit this inventory, what do we recover and what margin do we give up?' It's a structured way to discuss end-of-life inventory without making ad hoc decisions row by row in a spreadsheet."

**Point at:** Markdown percentage, disposition status, conditional formatting on disposition.

---

#### 5. Management Summary (~35 seconds)

**What to say:**

> "I close with a one-page executive summary that ties the story together — total inventory value, aged and excess exposure, transfer and markdown candidates, top risks, and a 30/60/90-day action plan.
>
> This is printable and designed for a director or VP who wants the headline without navigating every operational tab. It shows I can translate detailed analysis into a leadership-ready deliverable."

**Point at:** Inventory health KPIs, top 5 inventory risks, 30/60/90-day plan.

---

### Closing Statement (~20 seconds)

> "So my inventory workflow is: dashboard for visibility, exception analysis for focus, transfer before markdown, markdown when redeployment isn't enough, and a management summary for leadership. The same disciplined approach applies whether I'm supporting a tire retailer, a DC network, or any business trying to reduce aged inventory without sacrificing service levels."

---

### Likely Interviewer Questions & Strong Answers

**Q: How would you connect this to a live ERP or WMS?**

> "The structure mirrors how I would work in production: a clean master dataset, calculated status fields, exception tabs, and a summary layer. In an ERP, Master Inventory would map to item/location inventory tables; the dashboard KPIs would be SQL or BI measures; transfer and markdown tabs would be fed by replenishment and pricing rules. This Python version proves the logic and layout — integration is the next step, not a different approach."

**Q: How do you decide transfer versus markdown?**

> "Transfer first when another location has demand and the net benefit covers handling and freight. Markdown when age, demand, and sell-through show the item won't move at full price — or when holding cost exceeds recovery. The toolkit encodes that sequence explicitly so the business doesn't jump to discounting inventory that could still be sold elsewhere."

**Q: What KPI would you watch most closely in this demo?**

> "Aged inventory value and markdown candidate count together. Aged dollars tell me how much cash is tied up; markdown candidates tell me how much of that is already flagged for action. If those rise while stockout risk also rises, that's a sign the replenishment and allocation process — not just pricing — needs attention."

**Q: Is this real data?**

> "No — all sample data is fictional and generated for demo purposes. The scenarios are realistic — excess at one location, stockout risk elsewhere, slow movers, obsolete items — but no real company or customer information is included."

---

## Demo 2: IT Inventory Control Specialist

**Role focus:** IT asset management, audit readiness, lifecycle control, compliance  
**Suggested timing:** ~30 seconds per tab (6 tabs)

### Opening Statement (~20 seconds)

> "This side of the toolkit focuses on IT asset lifecycle control — from receiving and assignment through audit, software compliance, mobile provisioning, and secure disposal. I built it to show how I standardize asset tracking, surface exceptions early, and give leadership a clear picture of operational risk. Same principle as inventory: clean records, rule-based status, exception reporting, and a summary view."

---

### Tabs to Show

#### 1. IT Asset Register (~30 seconds)

**What to say:**

> "This is the system of record for IT assets — asset tag, serial number, device type, assigned user, location, warranty, status, and lifecycle stage.
>
> Conditional formatting highlights missing assets, warranty watch items, and lifecycle exceptions. Dropdown validations keep status values consistent. In an interview or operational setting, this is the tab that answers: 'What do we own, where is it, and who has it?'"

**Point at:** Status and lifecycle columns, conditional formatting, filterable table.

---

#### 2. Audit Reconciliation (~30 seconds)

**What to say:**

> "This tab compares system records against a physical audit sample and flags exceptions — missing from audit, found not in system, wrong location, wrong user, duplicate serial numbers, and retired-but-active assets.
>
> The KPI section shows total assets audited, exception count, exception rate, and open high-priority items. This is how I would run a quarterly audit follow-up: identify gaps, assign owners, and track resolution — not just produce a one-time report."

**Point at:** Exception KPI cards, exception type summary, priority formatting.

---

#### 3. Software Licenses (~30 seconds)

**What to say:**

> "License compliance is a common audit and budget risk. This tab tracks purchased versus assigned licenses, renewal dates, annual cost, and compliance status.
>
> Over-assigned licenses are highlighted in red; renewals due soon and renewal watch items use orange and yellow. The summary shows over-assignment count, renewals within 90 days, and total annual software spend. This supports both compliance conversations and budget planning."

**Point at:** Compliance status formatting, renewal summary KPIs, annual cost column.

---

#### 4. Mobile Provisioning (~30 seconds)

**What to say:**

> "Mobile devices need a consistent provisioning and recovery checklist — MDM enrolled, security configured, required apps installed, user agreement signed, and current status.
>
> The summary shows assigned devices, pending setup, missing user agreements, and returned devices. This standardizes field and corporate mobility control so devices don't fall through the cracks between HR, IT, and the help desk."

**Point at:** Yes/No checklist columns, pending setup / missing agreement highlights, summary KPIs.

---

#### 5. Disposal Log (~30 seconds)

**What to say:**

> "When assets are retired, control doesn't stop — data wipe, vendor disposal, and certificate of destruction matter for security and audit. This tab tracks wipe status, vendor, certificate received, and disposal status.
>
> Pending wipe and certificate missing are highlighted so nothing is disposed informally without documentation. That's especially important in regulated environments or any organization with data retention requirements."

**Point at:** Data wipe fields, certificate received, disposal status conditional formatting.

---

#### 6. Management Summary (~30 seconds)

**What to say:**

> "I close with the same leadership pattern as the inventory demo — a printable one-pager with IT asset KPIs, software license risks, top IT asset risks, and a 30/60/90-day action plan.
>
> This shows I can support both operational teams and management with the same underlying data — detailed tabs for technicians and analysts, summary tab for leadership."

**Point at:** IT asset control highlights, software license risks, top IT risks, action plan.

---

### Closing Statement (~20 seconds)

> "My IT asset approach is: one accurate register, regular audit reconciliation, proactive license and mobile compliance tracking, documented disposal, and a management summary that makes risk visible. Whether the organization uses ServiceNow, Intune, or spreadsheets today, the process — capture, validate, exception-manage, report — stays the same."

---

### Likely Interviewer Questions & Strong Answers

**Q: How would this integrate with ServiceNow or an MDM platform?**

> "Each tab maps to a standard ITAM workflow. The asset register is the CMDB or asset table; audit reconciliation is an exception queue from physical verification; software licenses map to SAM data; mobile provisioning maps to MDM enrollment status; disposal maps to retirement and certificate records. This workbook demonstrates the target operating model — integration would feed these views automatically rather than change the process."

**Q: How do you prioritize audit exceptions?**

> "High priority first: missing from audit, found not in system, retired but active, and duplicate serial numbers — those affect security, financial accuracy, and compliance. Medium priority: wrong location or wrong user, which may be data hygiene or actual movement issues. I would assign an owner and resolution status to every exception and track open items until closed, not just report them once."

**Q: How do you handle over-assigned software licenses?**

> "First, validate whether the assignment data is current — sometimes HR or procurement records lag. Then reconcile purchased entitlements against active assignments, reclaim unused licenses, and adjust purchasing on renewal. The tab flags over-assignment automatically so SAM review isn't dependent on someone noticing it in a flat export."

**Q: Why include disposal and mobile in the same toolkit as laptops and desktops?**

> "Because IT asset control isn't just hardware inventory — it's the full lifecycle and every device class that stores company data. Phones and retired equipment are common audit findings when they're managed separately. One toolkit with consistent status rules and exception reporting is easier to govern than disconnected spreadsheets."

**Q: Did you build this manually in Excel?**

> "No — the entire workbook is generated from Python using openpyxl. Business rules, sample data, styling, formulas, and validations are all in source code. That means I can regenerate the workbook, run tests against it, and extend it without hand-maintaining twelve tabs."

---

## Quick Reference: Which Demo to Use?

| Interview focus | Use this demo | Start on tab |
|-----------------|---------------|--------------|
| Inventory analyst, supply chain, warehouse, retail ops | Mavis Inventory Optimization | Inventory Dashboard |
| IT asset specialist, IT ops, audit, SAM, endpoint management | IT Inventory Control | IT Asset Register |
| General analyst / hybrid role | Either demo + mention the other path exists on README tab | README |

**Tip:** Open the workbook to the **README** tab before the interview starts. It contains demo paths, talking points, and the sample-data disclaimer — a strong first impression while you share your screen.
