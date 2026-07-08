# PRD.md

# Inventory Optimization AI Co-Pilot — Product Requirements Document

## 1. Product Overview

The Inventory Optimization AI Co-Pilot is an enterprise-style analytics application designed to help inventory, supply chain, procurement, and distribution teams identify unhealthy inventory and convert data into profitable operational action.

The application ingests inventory data from an Excel workbook or CSV files, calculates inventory health KPIs, flags aged/excess/slow-moving/obsolete inventory, recommends transfer or markdown actions, and generates AI-assisted executive summaries for leadership.

This product is designed as a presentation-ready prototype for an Inventory Optimization Analyst role at a large retail and distribution organization.

## 2. Product Positioning

This is not a generic dashboard and not a chatbot.

It is a decision-support tool that answers five business questions:

1. Where is inventory unhealthy?
2. Which SKUs and locations require action?
3. Should we transfer, markdown, replenish, monitor, or liquidate?
4. What is the financial impact of each action?
5. How should the recommendation be communicated to leadership?

## 3. Target Users

### Primary User: Inventory Optimization Analyst

Responsible for monitoring inventory health, identifying aged/excess inventory, building reporting, and recommending actions to improve inventory turnover, in-stock rates, margin recovery, and working capital efficiency.

### Secondary User: Procurement Manager

Uses the tool to understand where purchasing decisions may have created excess, obsolete, or slow-moving inventory.

### Secondary User: Distribution / DC Operations Manager

Uses the tool to review transfer recommendations, evaluate network balancing opportunities, and understand where inventory should move.

### Secondary User: Executive / Regional Leader

Uses the management summary to understand inventory risk, financial exposure, and recommended next actions without reviewing row-level data.

## 4. Business Problem

Large retail and distribution networks often hold inventory across stores, distribution centers, and regions. Inventory can become unhealthy when the wrong products sit in the wrong locations, demand shifts, products age, replenishment is misaligned, or markdowns are applied too late.

Common pain points include:

* Excess inventory tying up working capital
* Aged inventory losing value over time
* Stockout risk in some locations while other locations are overstocked
* Poor visibility into transfer opportunities
* Markdown decisions made without clear margin impact
* Analysts spending too much time manually summarizing data
* Leadership receiving reports without actionable recommendations

## 5. Product Goals

The application should:

1. Provide an executive-level inventory health dashboard.
2. Identify aged, excess, slow-moving, obsolete, and stockout-risk inventory.
3. Prioritize exception items by financial exposure and risk.
4. Recommend transfer actions before markdowns when economically justified.
5. Recommend markdown or liquidation actions when transfer is not viable.
6. Calculate financial impact, including recovery value, margin impact, transfer cost, and net benefit.
7. Generate AI-assisted plain-English summaries for leadership.
8. Maintain a clean, modular architecture suitable for demonstration in Cursor.
9. Include robust automated testing for data validation, KPI calculations, and recommendation logic.
10. Present with a polished enterprise UI/UX.

## 6. Non-Goals

The MVP does not need:

* Real-time ERP integration
* User authentication
* Production database deployment
* Live transportation carrier integration
* Complex machine learning forecasting
* Full demand planning engine
* Role-based permissions

These can be listed as future enhancements.

**In scope for this release:** Static cloud deployment on Vercel (browser-based Streamlit via Stlite), with OpenAI summaries proxied through a serverless API so API keys are not exposed in the browser.

## 7. MVP Scope

The MVP will include the following modules:

### 7.1 Executive Dashboard

The dashboard provides a high-level inventory health control tower.

Required KPIs:

* Total inventory value
* Aged inventory value
* Excess inventory value
* Slow-moving SKU count
* Obsolete SKU count
* Transfer candidate count
* Markdown candidate count
* Stockout risk count
* Estimated recovery value
* Average gross margin
* Inventory turnover
* GMROI
* Days of supply

Required visuals:

* Inventory value by location
* Inventory status breakdown
* Aging bucket summary
* Recommended action breakdown
* Top inventory risks by dollar exposure

### 7.2 Aged & Excess Inventory

The aged/excess module shows only exception items, not the full inventory dataset.

Required columns:

* SKU
* Product name
* Category
* Location
* Region
* On-hand quantity
* Min stock
* Max stock
* Excess quantity
* Inventory age days
* 90-day demand
* Average weekly sales
* Sell-through rate
* Days of supply
* Inventory value
* Gross margin
* Risk level
* Issue type
* Recommended action
* Analyst notes

Required behavior:

* Allow filtering by location, category, issue type, risk level, and recommended action.
* Sort by inventory value or financial exposure.
* Highlight high-risk rows.
* Show row-level recommendation explanation.

### 7.3 Transfer Planner

The transfer planner recommends movement of inventory from overstocked locations to locations with need or stronger demand.

Required columns:

* SKU
* Product name
* Source location
* Destination location
* Source excess quantity
* Destination need quantity
* Suggested transfer quantity
* Transfer cost per unit
* Total transfer cost
* Estimated margin protected
* Net benefit
* Recommendation
* Confidence level
* Explanation

Required behavior:

* Prioritize transfers by net benefit.
* Do not recommend transfers where cost exceeds expected benefit.
* Recommend transfers before markdowns when destination demand exists.
* Provide a clear explanation for each recommendation.

### 7.4 Markdown Planner

The markdown planner supports end-of-life and aged inventory exit strategies.

Required columns:

* SKU
* Product name
* Location
* Inventory age days
* Current retail price
* Unit cost
* Current margin
* Suggested markdown percent
* Markdown price
* Projected sell-through percent
* Estimated recovery value
* Margin impact
* Recommended disposition
* Explanation

Required behavior:

* Suggest smaller markdowns when sell-through remains moderate.
* Suggest deeper markdowns or liquidation when demand is near zero and age is high.
* Show estimated recovery value.
* Show margin impact.
* Avoid markdown recommendations when transfer has stronger net benefit.

### 7.5 AI Management Summary

The AI management summary converts analytical outputs into executive-ready language.

Required outputs:

* Weekly inventory health summary
* Top risks
* Recommended actions
* Transfer opportunities
* Markdown priorities
* 30/60/90-day action plan
* Cross-functional callouts for Procurement, Distribution, and Leadership

Important AI behavior:

* AI should not invent data.
* AI must summarize only calculated metrics and available records.
* AI should be used as a communication and reasoning aid, not as the sole decision-maker.
* The application must have a deterministic fallback summary for demo reliability.

**Provider modes:**

* **Local (offline template):** Always available; generates an executive summary from calculated KPIs without external APIs.
* **OpenAI (live LLM):** Uses structured metrics only. Locally, requires `OPENAI_API_KEY` in `.env.local`. In the cloud deployment, calls a secure Vercel serverless proxy (`/api/summary`) so the API key never ships to the browser.

**Cloud UX expectations:**

* OpenAI generation typically takes **15–45 seconds** in the browser; the UI shows a generating state and an instant offline baseline summary while waiting.
* Users should keep the tab open until generation completes.

### 7.6 Data Upload / Data Source

The app should support:

* Loading from the existing Excel workbook
* Loading from sample CSV files
* Graceful error messages if required columns are missing
* Validation before analytics calculations run
* **Cloud (Vercel/Stlite):** Embedded sample CSV; Excel workbooks are not loaded in the browser runtime

## 8. Deployment & Runtime Modes

The application supports two runtimes:

| Mode | Entry | Best for |
|------|-------|----------|
| **Local development** | `streamlit run streamlit_app.py` | Full Excel support, local OpenAI key, rapid iteration |
| **Cloud (production)** | https://mavis-inventory-ai-copilot-dusky.vercel.app | Interview demos, sharing without local setup |

Cloud architecture:

* **Frontend:** Stlite bundles Streamlit + Python (Pyodide) into a static `public/index.html`.
* **Backend:** Vercel serverless function at `/api/summary` proxies OpenAI Chat Completions.
* **Secrets:** `OPENAI_API_KEY` is set in Vercel project environment variables (Production), not in client code.

## 9. User Experience Requirements

The application should feel like an enterprise analytics solution.

### Visual Style

* Professional dark or light theme
* Clean KPI cards
* Consistent spacing
* Clear section headers
* Executive-friendly language
* Minimal visual clutter
* Business-focused labels
* Status badges for risk levels and actions

### Navigation

Recommended app navigation:

1. Executive Dashboard
2. Aged & Excess
3. Transfer Planner
4. Markdown Planner
5. AI Summary
6. Data Quality
7. Methodology

### UX Principles

* Start broad, then drill down.
* Show financial impact wherever possible.
* Avoid overwhelming users with raw data.
* Explain the recommendation, not just the calculation.
* Make filters easy to use.
* Make the AI summary easy to copy into an email or leadership update.

## 10. Data Requirements

The minimum inventory dataset should include:

* sku
* product_name
* category
* location
* location_type
* region
* on_hand_qty
* min_stock
* max_stock
* unit_cost
* retail_price
* inventory_age_days
* demand_90_day
* avg_weekly_sales
* discontinued_flag
* transfer_cost_per_unit

Derived fields:

* inventory_value
* gross_margin
* gross_margin_percent
* excess_qty
* days_of_supply
* sell_through_rate
* aged_flag
* excess_flag
* slow_moving_flag
* obsolete_flag
* stockout_risk_flag
* issue_type
* risk_level
* recommended_action
* estimated_recovery_value

## 11. Recommendation Logic

### Excess Inventory

Flag as excess when:

* on_hand_qty > max_stock

### Aged Inventory

Flag as aged when:

* inventory_age_days >= 180

### Slow-Moving Inventory

Flag as slow-moving when:

* demand_90_day is low relative to on-hand quantity
* sell-through rate is below threshold
* days of supply is high

### Obsolete Inventory

Flag as obsolete when:

* discontinued_flag = true
* demand_90_day = 0 or near zero
* inventory_age_days is very high

### Stockout Risk

Flag as stockout risk when:

* on_hand_qty < min_stock

### Transfer Recommendation

Recommend transfer when:

* Source location has excess inventory
* Destination location has stockout risk or demand need
* Same SKU exists across the network
* Estimated margin protected exceeds transfer cost
* Suggested transfer quantity is greater than zero

### Markdown Recommendation

Recommend markdown when:

* Inventory is aged, slow-moving, or obsolete
* Transfer is not economically justified
* Demand is weak but recovery value exists

### Liquidation Recommendation

Recommend liquidation when:

* Inventory is obsolete
* Demand is near zero
* Age is very high
* Markdown recovery is low

## 12. Testing Requirements

Testing is required for the MVP.

### Unit Tests

Must cover:

* KPI calculations
* Inventory value calculation
* Gross margin calculation
* Days of supply calculation
* Sell-through calculation
* Excess quantity calculation
* Risk classification
* Recommended action logic
* Transfer net benefit logic
* Markdown recommendation logic
* OpenAI proxy / browser HTTP helpers (local unit tests)

### End-to-End / Browser Tests

Optional scripts for cloud verification:

* `scripts/test_stlite_ai_summary.mjs` — Playwright test of AI Summary on production URL
* `scripts/test_browser_proxy_xhr.mjs` — sync XHR proxy smoke test

### Data Validation Tests

Must cover:

* Missing required columns
* Invalid numeric fields
* Negative inventory quantities
* Null SKU values
* Invalid prices
* Invalid demand values
* Duplicate SKU-location rows

### Integration Tests

Must cover:

* Loading the sample Excel workbook
* Transforming raw data into clean inventory records
* Running KPI calculations end-to-end
* Generating transfer recommendations
* Generating markdown recommendations
* Generating a management summary

### UI Smoke Tests

Must cover:

* App loads successfully
* Dashboard page renders
* Aged/excess page renders
* Transfer planner page renders
* Markdown planner page renders
* AI summary page renders

## 13. Acceptance Criteria

The MVP is complete when:

1. The app loads sample workbook data successfully (local) or embedded sample CSV (cloud).
2. The dashboard displays all required KPIs.
3. The aged/excess table filters and sorts correctly.
4. The transfer planner produces ranked transfer recommendations.
5. The markdown planner produces margin-aware markdown recommendations.
6. The AI summary generates a leadership-ready narrative (local template or OpenAI).
7. The app has deterministic fallback summary behavior.
8. Tests pass through `pytest` (63+ tests).
9. The codebase has a clean folder structure.
10. The UI is polished enough for an on-site interview demonstration.
11. **Cloud:** Production deploy on Vercel loads in the browser and OpenAI summaries work via `/api/summary` with server-side API key.

## 14. Demo Storyline

The demo should follow this sequence:

1. Start with the business problem.
2. Open the cloud app (https://mavis-inventory-ai-copilot-dusky.vercel.app) or run locally.
3. Show the Executive Dashboard.
4. Drill into Aged & Excess Inventory.
5. Explain how the app prioritizes exceptions.
6. Show Transfer Planner as the first action path.
7. Show Markdown Planner as the second action path.
8. On **AI Summary**, click **Generate Summary** and wait 15–45 seconds for the OpenAI narrative (cloud uses Vercel proxy; local can use `.env.local` key or offline template).
9. Close by explaining how this would connect to real Mavis data sources.

## 15. Future Enhancements

Future enhancements may include:

* ERP/WMS/POS integration
* SQL database backend
* User authentication
* Role-based dashboards
* Demand forecasting
* Seasonality detection
* Tire fitment demand modeling
* Route optimization
* Approval workflows
* Scheduled executive reports
* Email/Slack summary distribution
* Power BI export
* Snowflake or BigQuery integration
