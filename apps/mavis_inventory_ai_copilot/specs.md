# Specs.md

# Inventory Optimization AI Co-Pilot — Technical Specification

## 1. Technical Overview

The Inventory Optimization AI Co-Pilot is a Python-based enterprise analytics application built with Streamlit, Pandas, Plotly, Pydantic, and Pytest.

The application is designed for rapid local development in Cursor while maintaining a clean production-style architecture. Business logic is separated from UI code so calculations, recommendation rules, data validation, and AI summary generation can be tested independently.

The app also ships as a **static cloud deployment on Vercel**: Streamlit runs in the browser via Stlite/Pyodide, and OpenAI calls are proxied through a Vercel serverless function so API keys stay server-side.

## 2. Recommended Tech Stack

### Application

* Python 3.11+
* Streamlit
* Pandas
* NumPy
* Plotly
* OpenPyXL
* Pydantic
* Python-dotenv

### Testing

* Pytest
* Pytest-cov
* Pandas testing utilities
* Streamlit testing module, where available
* Ruff for linting
* Mypy for optional static type checks

### Optional AI Integrations

* OpenAI API (implemented — local direct call or Vercel proxy)
* Anthropic API (planned)
* Gemini API (planned)

The app must also include a local deterministic fallback summary generator so the demo does not depend on internet, API keys, or rate limits.

### Cloud Deployment

* Vercel (static Stlite bundle + Python serverless API)
* Stlite / `@stlite/browser` (Streamlit in Pyodide)
* stlitepack (build tool)

Production URL: https://mavis-inventory-ai-copilot-dusky.vercel.app

## 3. Proposed Project Structure

```text
inventory-optimization-ai-copilot/
  PRD.md
  Specs.md
  README.md
  requirements.txt
  requirements-stlite.txt      # Pyodide browser bundle deps
  requirements-api.txt         # Vercel serverless OpenAI proxy
  .env.example
  .gitignore
  vercel.json

  streamlit_app.py             # Canonical Streamlit entry (Vercel-safe name)
  app.py                       # Back-compat wrapper → streamlit_app.py

  api/
    summary.py                   # Vercel serverless OpenAI proxy

  public/
    index.html                   # Built Stlite bundle (generated)

  scripts/
    build_vercel_stlite.py       # Build public/index.html for Vercel
    test_stlite_ai_summary.mjs   # Playwright E2E (optional)
    test_browser_proxy_xhr.mjs   # Proxy smoke test (optional)

  .streamlit/
    config.toml
    secrets.toml                 # Placeholder for Stlite browser runtime

  data/
    raw/
      Inventory_IT_Asset_Control_Toolkit.xlsx
    sample/
      sample_inventory.csv
    processed/

  src/
    __init__.py

    config/
      __init__.py
      settings.py
      constants.py
      runtime.py                 # is_browser_runtime() for Pyodide/Stlite

    data/
      __init__.py
      loaders.py
      validators.py
      transformers.py
      sample_data.py

    models/
      __init__.py
      inventory.py
      recommendations.py
      kpis.py

    services/
      __init__.py
      kpi_dashboard_service.py
      inventory_health_service.py
      transfer_service.py
      markdown_service.py
      summary_service.py
      ai_service.py

    ui/
      __init__.py
      theme.py
      components.py
      layout.py
      pages/
        __init__.py
        dashboard.py
        aged_excess.py
        transfer_planner.py
        markdown_planner.py
        ai_summary.py
        data_quality.py
        methodology.py

    utils/
      __init__.py
      formatting.py
      logging.py
      exceptions.py
      browser_http.py            # Sync XHR for Pyodide; urllib locally

  tests/
    __init__.py
    conftest.py

    unit/
      test_kpi_service.py
      test_inventory_health_service.py
      test_transfer_service.py
      test_markdown_service.py
      test_summary_service.py
      test_ai_service.py
      test_browser_http.py
      test_validators.py

    integration/
      test_excel_loader.py
      test_pipeline.py

    ui/
      test_app_smoke.py
```

## 4. Architecture Principles

### 4.1 Separation of Concerns

The app must separate:

* UI rendering
* Data loading
* Data validation
* Data transformation
* KPI calculation
* Recommendation logic
* AI summary generation

Streamlit pages should call service functions. They should not contain business logic.

### 4.2 Deterministic Business Logic

Inventory recommendations must come from deterministic rules and calculations.

AI may explain, summarize, or rephrase recommendations, but AI must not be the only source of decision logic.

### 4.3 Demo Reliability

The app must work without external APIs.

If no API key is present, the app should use a local summary generator.

### 4.4 Testability

Every major business rule must have a test.

The app should support headless testing of:

* KPI calculations
* Inventory classification
* Transfer logic
* Markdown logic
* Summary generation
* Data validation

### 4.5 Dual Runtime Support

The codebase detects runtime via `src/config/runtime.py`:

* **Local Python:** `streamlit run streamlit_app.py` — full Excel, dotenv, direct OpenAI SDK.
* **Browser (Pyodide/Stlite):** `sys.platform == "emscripten"` — embedded CSV, sync XHR to `/api/summary`, no client-side API keys.

Browser HTTP must not use `asyncio.run()`, `urllib`, or async `pyfetch` from synchronous Streamlit callbacks. Use `src/utils/browser_http.py` (JS `XMLHttpRequest` via `pyodide.ffi.Function`).

## 5. Environment Variables

Create `.env.example` and load secrets from `.env.local` (gitignored) at repo root or app folder:

```text
APP_ENV=development
AI_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
DEFAULT_DATA_SOURCE=data/raw/Inventory_IT_Asset_Control_Toolkit.xlsx
```

Supported `AI_PROVIDER` values:

```text
local
openai
anthropic   # not yet implemented
gemini      # not yet implemented
```

**Local development:**

```text
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...   # in .env.local (gitignored)
```

**Vercel production:**

Set in project Settings → Environment Variables (Production):

```text
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini   # optional
```

The browser bundle never receives the OpenAI key; it POSTs structured metrics to `/api/summary`.

## 6. Data Model

### 6.1 InventoryRecord

```python
from pydantic import BaseModel, Field


class InventoryRecord(BaseModel):
    sku: str
    product_name: str
    category: str
    location: str
    location_type: str
    region: str
    on_hand_qty: float = Field(ge=0)
    min_stock: float = Field(ge=0)
    max_stock: float = Field(ge=0)
    unit_cost: float = Field(ge=0)
    retail_price: float = Field(ge=0)
    inventory_age_days: int = Field(ge=0)
    demand_90_day: float = Field(ge=0)
    avg_weekly_sales: float = Field(ge=0)
    discontinued_flag: bool
    transfer_cost_per_unit: float = Field(ge=0)
```

### 6.2 InventoryHealthRecord

Derived fields:

```python
inventory_value: float
gross_margin: float
gross_margin_percent: float
excess_qty: float
days_of_supply: float
sell_through_rate: float
aged_flag: bool
excess_flag: bool
slow_moving_flag: bool
obsolete_flag: bool
stockout_risk_flag: bool
issue_type: str
risk_level: str
recommended_action: str
recommendation_reason: str
```

### 6.3 TransferRecommendation

```python
sku: str
product_name: str
source_location: str
destination_location: str
source_excess_qty: float
destination_need_qty: float
suggested_transfer_qty: float
transfer_cost_per_unit: float
total_transfer_cost: float
estimated_margin_protected: float
net_benefit: float
recommendation: str
confidence_level: str
explanation: str
```

### 6.4 MarkdownRecommendation

```python
sku: str
product_name: str
location: str
inventory_age_days: int
current_retail_price: float
unit_cost: float
current_margin: float
suggested_markdown_pct: float
markdown_price: float
projected_sell_through_pct: float
estimated_recovery_value: float
margin_impact: float
recommended_disposition: str
explanation: str
```

## 7. Required Input Columns

The app should normalize incoming columns into the following canonical names:

```text
sku
product_name
category
location
location_type
region
on_hand_qty
min_stock
max_stock
unit_cost
retail_price
inventory_age_days
demand_90_day
avg_weekly_sales
discontinued_flag
transfer_cost_per_unit
```

## 8. Data Validation Rules

Validation must run before analytics calculations.

### Required Column Validation

Fail gracefully if required columns are missing.

### Numeric Validation

The following fields must be numeric and non-negative:

```text
on_hand_qty
min_stock
max_stock
unit_cost
retail_price
inventory_age_days
demand_90_day
avg_weekly_sales
transfer_cost_per_unit
```

### Business Validation

The app should warn, but not necessarily fail, when:

* retail_price < unit_cost
* max_stock < min_stock
* avg_weekly_sales = 0 while demand_90_day > 0
* duplicated SKU-location pairs exist
* discontinued_flag has unexpected values

## 9. KPI Calculation Specifications

### 9.1 Inventory Value

```text
inventory_value = on_hand_qty * unit_cost
```

### 9.2 Gross Margin

```text
gross_margin = retail_price - unit_cost
```

### 9.3 Gross Margin Percent

```text
gross_margin_percent = gross_margin / retail_price
```

When retail price is zero, return zero.

### 9.4 Excess Quantity

```text
excess_qty = max(on_hand_qty - max_stock, 0)
```

### 9.5 Days of Supply

```text
days_of_supply = on_hand_qty / avg_daily_sales
avg_daily_sales = avg_weekly_sales / 7
```

When average weekly sales is zero:

```text
days_of_supply = 999
```

### 9.6 Sell-Through Rate

```text
sell_through_rate = demand_90_day / (demand_90_day + on_hand_qty)
```

When denominator is zero, return zero.

### 9.7 Inventory Turnover

```text
inventory_turnover = annualized_cogs / average_inventory_value
```

For MVP approximation:

```text
annualized_cogs = demand_90_day * 4 * unit_cost
average_inventory_value = inventory_value
```

### 9.8 GMROI

```text
GMROI = gross_margin_dollars / average_inventory_cost
```

For MVP approximation:

```text
gross_margin_dollars = demand_90_day * gross_margin
average_inventory_cost = inventory_value
```

When inventory value is zero, return zero.

## 10. Inventory Health Classification

### 10.1 Aged

```text
inventory_age_days >= 180
```

### 10.2 Excess

```text
on_hand_qty > max_stock
```

### 10.3 Slow-Moving

```text
days_of_supply >= 120
and sell_through_rate < 0.25
and demand_90_day > 0
```

### 10.4 Obsolete

```text
discontinued_flag = true
or inventory_age_days >= 365
or demand_90_day = 0 and inventory_age_days >= 240
```

### 10.5 Stockout Risk

```text
on_hand_qty < min_stock
```

## 11. Issue Type Logic

Issue type priority:

1. Obsolete
2. Excess/Aged
3. Stockout Risk
4. Excess
5. Slow-Moving
6. Aged
7. Healthy

Rules:

```text
If obsolete_flag:
    issue_type = "Obsolete"

Else if excess_flag and aged_flag:
    issue_type = "Excess/Aged"

Else if stockout_risk_flag:
    issue_type = "Stockout Risk"

Else if excess_flag:
    issue_type = "Excess"

Else if slow_moving_flag:
    issue_type = "Slow-Moving"

Else if aged_flag:
    issue_type = "Aged"

Else:
    issue_type = "Healthy"
```

## 12. Risk Level Logic

### High Risk

```text
issue_type in ["Obsolete", "Excess/Aged"]
or inventory_value >= 10000
or inventory_age_days >= 365
```

### Medium Risk

```text
issue_type in ["Excess", "Slow-Moving", "Aged", "Stockout Risk"]
or inventory_value >= 5000
```

### Low Risk

```text
issue_type = "Healthy"
or inventory_value < 5000
```

## 13. Recommended Action Logic

Action priority:

1. Replenish
2. Review Transfer
3. Review Markdown
4. Liquidate
5. Monitor

Rules:

```text
If stockout_risk_flag:
    recommended_action = "Replenish"

Else if excess_flag and demand exists elsewhere:
    recommended_action = "Review Transfer"

Else if obsolete_flag and demand_90_day == 0:
    recommended_action = "Liquidate"

Else if aged_flag or slow_moving_flag or excess_flag:
    recommended_action = "Review Markdown"

Else:
    recommended_action = "Monitor"
```

Because demand elsewhere requires network comparison, the base inventory health service may initially assign:

```text
"Review Transfer or Markdown"
```

The transfer and markdown services will refine the action.

## 14. Transfer Recommendation Logic

### 14.1 Source Eligibility

A location can be a source when:

```text
source.on_hand_qty > source.max_stock
source.excess_qty > 0
```

### 14.2 Destination Eligibility

A location can be a destination when:

```text
destination.on_hand_qty < destination.min_stock
or destination.days_of_supply < 30
```

### 14.3 Suggested Transfer Quantity

```text
destination_need_qty = max(destination.min_stock - destination.on_hand_qty, 0)

suggested_transfer_qty = min(
    source.excess_qty,
    destination_need_qty
)
```

If destination need is zero but demand is strong:

```text
suggested_transfer_qty = min(
    source.excess_qty,
    max(destination.avg_weekly_sales * 4 - destination.on_hand_qty, 0)
)
```

### 14.4 Transfer Cost

```text
total_transfer_cost = suggested_transfer_qty * transfer_cost_per_unit
```

### 14.5 Estimated Margin Protected

```text
estimated_margin_protected = suggested_transfer_qty * gross_margin
```

### 14.6 Net Benefit

```text
net_benefit = estimated_margin_protected - total_transfer_cost
```

### 14.7 Transfer Recommendation

```text
If net_benefit > 0 and suggested_transfer_qty > 0:
    recommendation = "Transfer Recommended"

Else:
    recommendation = "Do Not Transfer"
```

### 14.8 Confidence Level

```text
If net_benefit >= 5000:
    confidence_level = "High"

Else if net_benefit >= 1000:
    confidence_level = "Medium"

Else:
    confidence_level = "Low"
```

## 15. Markdown Recommendation Logic

### 15.1 Markdown Percent

```text
If obsolete_flag or inventory_age_days >= 365:
    suggested_markdown_pct = 0.40

Else if inventory_age_days >= 240 and sell_through_rate < 0.10:
    suggested_markdown_pct = 0.30

Else if inventory_age_days >= 180 and sell_through_rate < 0.25:
    suggested_markdown_pct = 0.20

Else:
    suggested_markdown_pct = 0.10
```

### 15.2 Markdown Price

```text
markdown_price = retail_price * (1 - suggested_markdown_pct)
```

### 15.3 Projected Sell-Through Percent

```text
If suggested_markdown_pct >= 0.40:
    projected_sell_through_pct = 0.75

Else if suggested_markdown_pct >= 0.30:
    projected_sell_through_pct = 0.60

Else if suggested_markdown_pct >= 0.20:
    projected_sell_through_pct = 0.45

Else:
    projected_sell_through_pct = 0.30
```

### 15.4 Estimated Recovery Value

```text
estimated_recovery_value = on_hand_qty * markdown_price * projected_sell_through_pct
```

### 15.5 Margin Impact

```text
margin_impact = on_hand_qty * (retail_price - markdown_price)
```

### 15.6 Recommended Disposition

```text
If obsolete_flag and demand_90_day == 0:
    recommended_disposition = "Liquidate"

Else if suggested_markdown_pct >= 0.30:
    recommended_disposition = "Aggressive Markdown"

Else if suggested_markdown_pct >= 0.20:
    recommended_disposition = "Controlled Markdown"

Else:
    recommended_disposition = "Monitor / Light Markdown"
```

## 16. AI Summary Service

The AI service exposes one public function:

```python
generate_management_summary(
    kpis: dict,
    top_risks: list[dict],
    transfer_summary: dict,
    markdown_summary: dict,
    provider: str = "local",
    openai_api_key: str | None = None,
) -> str
```

### 16.1 Local Provider

The local provider uses templates and calculated values. It always works offline.

### 16.2 OpenAI Provider

**Local runtime:** Uses the OpenAI Python SDK with `OPENAI_API_KEY` from environment or session input.

**Browser runtime:** Calls `post_json("/api/summary", payload)` which:

1. Resolves relative URL against `js.location.origin`
2. POSTs JSON via synchronous `XMLHttpRequest` (safe inside Streamlit's event loop)
3. Returns `{ "summary": "..." }` from the Vercel handler

**Serverless proxy (`api/summary.py`):**

* Validates `OPENAI_API_KEY` from Vercel env
* Accepts `{ "model": "...", "context": { kpis, top_risks, ... } }`
* Calls OpenAI Chat Completions with a fixed system prompt and structured user payload
* Returns JSON with CORS headers for the Stlite origin

### 16.3 AI Summary Page UX

* **OpenAI in cloud:** Two-step generate (button → rerun → API call) with visible "Generating… 15–45 seconds" messaging
* **Baseline expander:** Instant offline template summary while waiting for OpenAI
* **Download:** Markdown export of generated summary

### 16.4 AI Guardrails

The AI summary must:

* Mention that recommendations are based on current sample data.
* Avoid claiming certainty beyond the data.
* Avoid inventing SKUs, values, or locations.
* Use calculated KPIs only.
* Recommend human review for final approval.

## 17. UI Specification

## 17.1 Global Layout

Use a wide layout.

Main sections:

* Header
* Sidebar navigation
* KPI row
* Filter panel
* Main content area
* Data table
* Recommendation explanation panel

## 17.2 Header

Header text:

```text
Inventory Optimization AI Co-Pilot
```

Subtitle:

```text
Enterprise inventory health, transfer optimization, markdown planning, and AI-assisted leadership summaries.
```

## 17.3 Sidebar

Sidebar items:

```text
Executive Dashboard
Aged & Excess
Transfer Planner
Markdown Planner
AI Summary
Data Quality
Methodology
```

Sidebar should include:

* Data source status
* Last refresh timestamp
* Row count
* Exception count
* Mode indicator (local OpenAI / offline demo / cloud Stlite)

## 17.4 KPI Cards

KPI cards should include:

* Label
* Value
* Delta or context
* Status color

Color rules:

```text
High risk = red
Medium risk = amber
Low risk / healthy = green
Neutral = blue or gray
```

## 17.5 Tables

Tables should support:

* Filtering
* Sorting
* Currency formatting
* Percentage formatting
* Conditional formatting through styled DataFrames where practical

## 17.6 Charts

Recommended charts:

* Bar chart: inventory value by location
* Donut chart: inventory status breakdown
* Bar chart: top risks by inventory value
* Bar chart: net benefit by transfer recommendation
* Bar chart: estimated recovery by markdown recommendation

## 18. Testing Strategy

Testing is required before demo.

## 18.1 Unit Tests

### KPI Tests

File:

```text
tests/unit/test_kpi_service.py
```

Required tests:

```text
test_inventory_value_calculation
test_gross_margin_calculation
test_gross_margin_percent_handles_zero_price
test_days_of_supply_normal_case
test_days_of_supply_zero_sales_returns_999
test_sell_through_rate_normal_case
test_sell_through_rate_zero_denominator
test_gmroi_calculation
test_gmroi_zero_inventory_value
```

### Inventory Health Tests

File:

```text
tests/unit/test_inventory_health_service.py
```

Required tests:

```text
test_excess_flag_when_on_hand_exceeds_max_stock
test_aged_flag_at_180_days
test_slow_moving_flag
test_obsolete_flag_for_discontinued_item
test_stockout_risk_when_below_min_stock
test_issue_type_priority_obsolete_before_excess
test_risk_level_high_for_high_value_excess_aged
test_recommended_action_replenish_for_stockout
```

### Transfer Tests

File:

```text
tests/unit/test_transfer_service.py
```

Required tests:

```text
test_source_eligibility_with_excess_qty
test_destination_eligibility_with_low_stock
test_suggested_transfer_qty_uses_min_of_source_and_need
test_total_transfer_cost
test_estimated_margin_protected
test_net_benefit
test_transfer_recommended_when_net_benefit_positive
test_no_transfer_when_cost_exceeds_benefit
```

### Markdown Tests

File:

```text
tests/unit/test_markdown_service.py
```

Required tests:

```text
test_obsolete_item_gets_40_percent_markdown
test_aged_low_sellthrough_item_gets_30_percent_markdown
test_moderate_aged_item_gets_20_percent_markdown
test_light_markdown_default
test_markdown_price
test_estimated_recovery_value
test_liquidation_disposition_for_obsolete_zero_demand
```

### Summary Tests

File:

```text
tests/unit/test_summary_service.py
```

Required tests:

```text
test_local_summary_generates_text
test_summary_includes_total_inventory_value
test_summary_includes_top_risk_count
test_summary_does_not_fail_with_empty_recommendations
```

### AI Service Tests

File:

```text
tests/unit/test_ai_service.py
```

Covers OpenAI key validation, API response handling, and error paths.

### Browser HTTP Tests

File:

```text
tests/unit/test_browser_http.py
```

Covers sync XHR path, URL resolution, and proxy integration mocks.

## 18.2 Data Validation Tests

File:

```text
tests/unit/test_validators.py
```

Required tests:

```text
test_missing_required_columns_returns_error
test_negative_inventory_qty_returns_error
test_null_sku_returns_error
test_duplicate_sku_location_returns_warning
test_retail_price_below_cost_returns_warning
test_max_stock_below_min_stock_returns_warning
```

## 18.3 Integration Tests

File:

```text
tests/integration/test_pipeline.py
```

Required tests:

```text
test_sample_data_loads
test_pipeline_generates_health_records
test_pipeline_generates_kpis
test_pipeline_generates_transfer_recommendations
test_pipeline_generates_markdown_recommendations
test_pipeline_generates_management_summary
```

## 18.4 UI Smoke Tests

File:

```text
tests/ui/test_app_smoke.py
```

Required tests:

```text
test_app_imports_without_error
test_pages_import_without_error
```

Optional Streamlit AppTest tests:

```text
test_dashboard_page_renders
test_ai_summary_page_renders
```

## 19. Commands

### Install Dependencies (local)

```bash
pip install -r requirements.txt
```

### Run App (local)

```bash
streamlit run streamlit_app.py
# or: streamlit run app.py
```

### Run Tests

```bash
pytest
```

Expected: **63+ passing tests**.

### Build Vercel Stlite Bundle

```bash
python scripts/build_vercel_stlite.py
```

Outputs `public/index.html`. The build script:

* Embeds `src/`, sample CSV, and `.streamlit/` config via stlitepack
* Escapes JS template literals in embedded Python (backslashes, `${`, backticks)
* Validates embedded Python compiles after JS simulation
* Validates browser HTTP code avoids asyncio/urllib in Pyodide path

### Deploy to Vercel

```bash
vercel deploy --prod --scope dac-004
```

Requires `OPENAI_API_KEY` in Vercel project env (Production).

### Optional E2E (cloud)

```bash
node scripts/test_stlite_ai_summary.mjs
```

### Run Tests With Coverage

```bash
pytest --cov=src --cov-report=term-missing
```

### Run Linting

```bash
ruff check .
```

### Run Formatting

```bash
ruff format .
```

## 20. Dependency Files

**Local / dev (`requirements.txt`):** Streamlit, Pandas, OpenPyXL, OpenAI, pytest, etc.

**Stlite browser (`requirements-stlite.txt`):**

```text
pandas
numpy
plotly
pydantic
```

**Vercel API (`requirements-api.txt`):**

```text
openai>=1.40.0
```

## 21. README Demo Script

The README should include:

```text
1. Open https://mavis-inventory-ai-copilot-dusky.vercel.app (or streamlit run streamlit_app.py locally)
2. Start on Executive Dashboard
3. Explain total inventory value, aged inventory, excess exposure, and recovery opportunity
4. Open Aged & Excess to show exception prioritization
5. Open Transfer Planner to show network balancing
6. Open Markdown Planner to show margin-aware exit strategy
7. Open AI Summary → Generate Summary (wait 15–45s in cloud for OpenAI narrative)
8. Close by explaining real-world data integration opportunities
```

## 22. Definition of Done

The build is complete when:

* App launches locally and on Vercel
* Sample data loads successfully (Excel locally, CSV in cloud)
* All pages render
* Dashboard KPIs calculate correctly
* Exception inventory is classified correctly
* Transfer recommendations are generated
* Markdown recommendations are generated
* AI summary works in local fallback mode and via OpenAI (local + Vercel proxy)
* Tests pass (63+)
* UI looks polished and enterprise-ready
* Code structure is clean enough to explain during the interview
