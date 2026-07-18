# Data Dictionary — Inventory Optimization Copilot v2.0.0

Field and metric definitions for generated datasets and workbook tabs. **Canonical column order:** `src/domain/schemas.py` → `INVENTORY_COLUMN_ORDER`.

---

## 1. Master Inventory (Phase 1 ✅)

| Field | Type | Description | Source / Formula |
|-------|------|-------------|------------------|
| item_id | string | Surrogate primary key | Generated `INV-####` |
| sku | string | Stock keeping unit | Product catalog |
| product_name | string | Display name | Fictional catalog |
| category | string | Top-level category | e.g., Tires, Filters |
| subcategory | string | Sub-category | e.g., All-Season, Oil |
| location | string | Site code | DC-* or Store-* |
| location_type | string | Distribution Center / Retail Store | Location map |
| region | string | Geographic rollup | Northeast, NYC Metro, etc. |
| quantity_on_hand | integer | Current units ≥ 0 | Generated |
| min_stock | integer | Minimum target | Generated |
| max_stock | integer | Maximum target | Generated |
| unit_cost | decimal | Unit cost USD | Catalog + noise |
| selling_price | decimal | Retail/list price USD | Markup on cost |
| total_value | decimal | Inventory value USD | `quantity_on_hand × unit_cost` |
| last_movement_date | date | Last warehouse movement | ≤ AS_OF_DATE |
| last_sale_date | date | Last sale date | ≤ AS_OF_DATE |
| age_days | integer | Days since last sale | `AS_OF_DATE - last_sale_date` |
| demand_90_day | integer | Units demanded in 90 days | Generated |
| sell_through_rate | decimal | 0–1 ratio | See BUSINESS_RULES §1 |
| gross_margin_pct | decimal | 0–1 ratio | `(selling_price - unit_cost) / selling_price` |
| status | string | Health classification | `assign_status_and_action()` |
| recommended_action | string | Next best action | `assign_status_and_action()` |

### Status enum

`Healthy`, `Stockout Risk`, `Excess`, `Slow-Moving`, `Excess / Aged`, `Obsolete`

### Recommended action enum

`Monitor`, `Replenish`, `Review Transfer`, `Transfer or Markdown`, `Markdown Review`, `Liquidate`

---

## 2. Aged Excess Analysis (Phase 1 ✅)

| Field | Type | Description |
|-------|------|-------------|
| SKU | string | From master |
| Product Name | string | From master |
| Location | string | From master |
| Quantity On Hand | integer | From master |
| Max Stock | integer | From master |
| Excess Quantity | integer | `max(qty - max_stock, 0)` |
| Age Days | integer | From master |
| 90 Day Demand | integer | From master |
| Sell Through Rate | decimal | From master |
| Inventory Value | decimal | Same as `total_value` |
| Risk Level | string | High / Medium / Low |
| Issue Type | string | Mapped from status |
| Recommended Action | string | From master |
| Analyst Notes | string | Static guidance by status |

---

## 3. Markdown Planner (Phase 1 ✅)

| Field | Type | Description |
|-------|------|-------------|
| SKU | string | Eligible SKU |
| Product Name | string | |
| Location | string | |
| Quantity On Hand | integer | |
| Unit Cost | decimal | USD |
| Current Selling Price | decimal | USD |
| Current Margin % | decimal | From master |
| Age Days | integer | |
| Demand Trend | string | No Demand / Declining / Slow / Moderate |
| Suggested Markdown % | decimal | 0.00–0.30 |
| Markdown Price | decimal | `price × (1 - markdown_pct)` |
| Projected Sell Through % | decimal | After markdown uplift |
| Estimated Recovery Value | decimal | USD |
| Margin Impact | decimal | USD delta |
| Recommended Disposition | string | Hold, Transfer First, 10%/20% Markdown, Liquidate |

---

## 4. Transfer Planner (Phase 1 ✅)

| Field | Type | Description |
|-------|------|-------------|
| SKU | string | Source SKU |
| Product Name | string | |
| Source Location | string | Excess location |
| Destination Location | string | Need location |
| Source Quantity | integer | On hand at source |
| Destination Quantity | integer | On hand at destination |
| Destination Min Stock | integer | |
| Destination Demand | integer | 90-day demand at destination |
| Suggested Transfer Quantity | integer | Computed move qty |
| Unit Cost | decimal | USD |
| Transfer Cost | decimal | Lane-based estimate USD |
| Estimated Margin Protected | decimal | USD |
| Net Benefit | decimal | `margin_protected - transfer_cost` |
| Recommendation | string | Transfer Recommended / Review Transfer |

---

## 5. Dashboard KPIs (Phase 1 ✅)

| KPI | Unit | Definition |
|-----|------|------------|
| Total Inventory Value | USD | Sum master total_value |
| Aged Inventory Value | USD | Sum where age_days > 180 |
| Excess Inventory Value | USD | Sum where status is Excess or Excess / Aged |
| Slow-Moving SKU Count | count | Status = Slow-Moving |
| Obsolete SKU Count | count | Status = Obsolete |
| Transfer Candidate Count | count | Action in transfer action set |
| Markdown Candidate Count | count | Action in markdown action set |
| Stockout Risk Count | count | Status = Stockout Risk |
| Estimated Recovery Value | USD | Sum value for markdown-related actions |
| Average Gross Margin % | % | Mean of gross_margin_pct |

### Dashboard chart dimensions

| Chart | Dimensions |
|-------|------------|
| Value by Location | location, inventory_value |
| Status Breakdown | status, sku_count, inventory_value |
| Aging Buckets | 0–90, 91–180, 181–365, 365+ days |
| Action Summary | recommended_action, sku_count, inventory_value |
| Top 10 Excess | sku, product_name, location, excess_qty, excess_value |

---

## 6. Management Summary (Phase 1 ✅)

| Element | Content |
|---------|---------|
| Metadata | Title, version, as-of date, author |
| KPI strip | 5 metrics (subset of dashboard) |
| Top risks | SKU, Location, Issue, Value (top 5 from aged/excess) |
| Action counts | recommended_action tallies |
| Action plan | 30/60/90-day placeholder bullets |

---

## 7. Planned — Inventory Classification (Prompt 04)

| Field | Type | Description |
|-------|------|-------------|
| SKU | string | |
| Annual Usage Value | decimal | Proxy from 90-day demand |
| Cumulative Usage % | decimal | Running Pareto |
| ABC Class | string | A / B / C |
| Demand CV | decimal | Coefficient of variation |
| XYZ Class | string | X / Y / Z |
| Combined Segment | string | e.g., AX, BY |
| Review Frequency | string | Weekly / Monthly / Quarterly |

---

## 8. Planned — Cycle Count Plan (Prompt 05)

| Field | Type | Description |
|-------|------|-------------|
| Location | string | |
| SKU | string | |
| ABC Class | string | From classification |
| Last Count Date | date | Fictional |
| Days Since Count | integer | |
| Inventory Value | decimal | |
| Risk Level | string | |
| Count Priority | integer | 1 = highest |
| Scheduled Week | string | ISO week label |
| Assignee | string | Fictional name |

---

## 9. Planned — Replenishment Planning (Prompt 06)

| Field | Type | Description |
|-------|------|-------------|
| SKU | string | |
| Location | string | |
| On Hand | integer | |
| Avg Daily Demand | decimal | `demand_90_day / 90` |
| Lead Time Days | integer | Default 14 |
| Safety Stock | decimal | See BUSINESS_RULES |
| Reorder Point | decimal | |
| EOQ | integer | Economic order quantity |
| Projected Stockout Date | date | |
| Suggested Order Qty | integer | |
| Order By Date | date | |

---

## 10. Planned — Demand Forecast (Prompt 07)

| Field | Type | Description |
|-------|------|-------------|
| SKU | string | |
| Location | string | |
| Historical Demand | integer | Baseline period |
| Forecast Method | string | e.g., Moving Average |
| Forecast W+1 … W+12 | integer | Weekly buckets |
| Seasonality Index | decimal | |
| Confidence | string | High / Medium / Low |

---

## 11. Planned — Service Level Analysis (Prompt 08)

| Field | Type | Description |
|-------|------|-------------|
| SKU | string | |
| Location | string | |
| Target Service Level % | decimal | |
| Actual Fill Rate % | decimal | |
| Stockout Events | integer | Days below min |
| Lost Sales Units | integer | Estimated |
| Service Level Gap | decimal | Target − actual |
| Action | string | |

---

## 12. Planned — Purchase Order Tracker (Prompt 08)

| Field | Type | Description |
|-------|------|-------------|
| PO Number | string | |
| Vendor | string | |
| SKU | string | |
| Order Qty | integer | |
| Received Qty | integer | |
| Open Qty | integer | `order - received` |
| Order Date | date | |
| Expected Receipt | date | |
| Status | string | Open / Partial / Closed / Late |
| Days Late | integer | |
| Buyer | string | Fictional |

---

## 13. Planned — Vendor Scorecards (Prompt 09)

| Field | Type | Description |
|-------|------|-------------|
| Vendor | string | |
| On-Time Delivery % | decimal | |
| Fill Rate % | decimal | |
| Quality Accept Rate % | decimal | |
| Avg Lead Time Days | integer | |
| YTD Spend | decimal | USD |
| Score | decimal | 0–100 weighted |
| Tier | string | Preferred / Approved / Probation / Review |
| Review Action | string | |

---

## 14. Generated CSV Schema

**File:** `data/generated/inventory_data.csv`  
**Columns:** Same as Master Inventory (snake_case headers matching `INVENTORY_COLUMN_ORDER`).

---

## 15. Workbook Metadata

| Property | Value |
|----------|-------|
| Title | Inventory Optimization Copilot |
| Creator | Daniel A. Cruz |
| Subject | Inventory Optimization |
| Version | v2.0.0 |

---

## Related Documents

- [BUSINESS_RULES.md](BUSINESS_RULES.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
