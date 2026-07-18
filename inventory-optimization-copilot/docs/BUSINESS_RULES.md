# Business Rules — Inventory Optimization Copilot v2.0.0

Authoritative rule definitions for Phase 1 (implemented) and planned Phase 2 sheets. **Implementation:** `src/services/` and `config/workbook_config.py`. Sheet builders must not reimplement these rules.

**Global constants:** `AS_OF_DATE = 2026-07-01`, `RANDOM_SEED = 42`.

---

## Rule Priority Overview

When multiple conditions could apply, **earlier rules win**. Lower number = higher priority.

| Priority | Domain | Rule set |
|----------|--------|----------|
| 1 | Master Inventory | Status & recommended action |
| 2 | Aged Excess | Risk level & issue type |
| 3 | Markdown Planner | Disposition & markdown % |
| 4 | Transfer Planner | Transfer recommendation |
| 5 | Dashboard | KPI inclusion filters |
| 6 | Planned | ABC, replenishment, service level |

---

## 1. Master Inventory — Status (Phase 1 ✅)

**Module:** `src/services/inventory_metrics.py` → `assign_status_and_action()`  
**Config:** `INVENTORY_THRESHOLDS`

Evaluate **in order**; first match sets `(status, recommended_action)`:

| # | Condition | Status | Recommended Action |
|---|-----------|--------|-------------------|
| 1 | `quantity_on_hand < min_stock` | Stockout Risk | Replenish |
| 2 | `age_days > 365` **and** `demand_90_day == 0` | Obsolete | Liquidate |
| 3 | `quantity_on_hand > max_stock` **and** `age_days > 180` | Excess / Aged | Transfer or Markdown |
| 4 | `quantity_on_hand > max_stock` | Excess | Review Transfer |
| 5 | `age_days > 180` **and** `sell_through_rate < 0.15` | Slow-Moving | Markdown Review |
| 6 | *(default)* | Healthy | Monitor |

### Supporting calculations (same module)

| Metric | Rule |
|--------|------|
| Sell-through | `demand_90_day / (quantity_on_hand + demand_90_day)`, max 1.0, denom 0 → 0 |
| Gross margin % | `(selling_price - unit_cost) / selling_price`, price ≤ 0 → 0 |
| Total value | `quantity_on_hand × unit_cost` (at generation) |
| Age days | Days from `last_sale_date` to `AS_OF_DATE`, min 0 |

---

## 2. Aged Excess Analysis (Phase 1 ✅)

**Module:** `src/services/inventory_health_service.py`

### 2.1 Row inclusion

Include rows where **Risk Level ≠ Low** (i.e., exclude Healthy-equivalent low risk).

### 2.2 Excess quantity

```text
excess_quantity = max(quantity_on_hand - max_stock, 0)
```

### 2.3 Risk level (from status)

| Status | Risk Level |
|--------|------------|
| Obsolete, Excess / Aged, Stockout Risk | High |
| Excess, Slow-Moving | Medium |
| Healthy | Low |

### 2.4 Issue type (from status)

| Status | Issue Type |
|--------|------------|
| Stockout Risk | Stockout Risk |
| Obsolete | Obsolete |
| Excess / Aged | Excess / Aged |
| Excess | Excess |
| Slow-Moving | Slow-Moving |
| Healthy | Within Target |

### 2.5 Analyst notes

Static guidance map in `src/domain/constants.py` → `ANALYST_NOTES` keyed by status.

### 2.6 Sort order

1. Risk level: High → Medium → Low  
2. Inventory value: descending

---

## 3. Markdown Planner (Phase 1 ✅)

**Module:** `src/services/markdown_service.py`  
**Config:** `MARKDOWN_THRESHOLDS`

### 3.1 Eligibility

Include rows where `status ∈ {Slow-Moving, Excess, Excess / Aged, Obsolete}`.

### 3.2 Disposition rules (first match)

| # | Condition | Markdown % | Disposition |
|---|-----------|------------|-------------|
| 1 | `age_days > 365` and `demand_90_day == 0` | 30% | Liquidate |
| 2 | `age_days > 270` | 20% | 20% Markdown |
| 3 | `age_days > 180` | 10% | 10% Markdown |
| 4 | `status == Excess` | 0% | Transfer First |
| 5 | default | 0% | Hold |

### 3.3 Demand trend

| Condition | Label |
|-----------|-------|
| `demand_90_day == 0` | No Demand |
| `sell_through_rate < 0.10` | Declining |
| `sell_through_rate < 0.20` | Slow |
| else | Moderate |

### 3.4 Projected sell-through

```text
if markdown_pct == 0:
    projected = current_sell_through
else:
    projected = min(current_sell_through + markdown_pct × 0.45, 0.90)
```

### 3.5 Recovery & margin impact

```text
markdown_price = selling_price × (1 - markdown_pct)
recovery_value = quantity_on_hand × markdown_price × projected_sell_through
margin_impact = projected_margin_dollars - current_margin_dollars
```

### 3.6 Sort

Disposition priority (Liquidate first) then Estimated Recovery Value descending.

---

## 4. Transfer Planner (Phase 1 ✅)

**Module:** `src/services/transfer_service.py`  
**Config:** `TRANSFER_SETTINGS`

### 4.1 Source qualification

Source row: `quantity_on_hand > max_stock` (has excess).

### 4.2 Destination qualification

Destination needs stock when **either**:

- `quantity_on_hand < min_stock` **and** `demand_90_day > 0`, **or**
- `demand_90_day >= 8` (strong demand threshold)

### 4.3 Destination matching

For each source, evaluate destinations with:

- Same SKU at different location, **or**
- Same category + subcategory (substitute SKU) at different location

Deduplicate by `item_id`; skip duplicate lane keys.

### 4.4 Suggested transfer quantity

```text
source_excess = quantity_on_hand - max_stock
shortage = max(min_stock - destination_on_hand, 0)
demand_need = floor(demand_90_day / 4) if strong_demand else 0
destination_need = shortage + destination_demand_buffer + demand_need
suggested_qty = max(min(source_excess, destination_need), 0)
```

`destination_demand_buffer = 5` (config).

### 4.5 Economics

```text
transfer_cost = lane_base + suggested_qty × per_unit   # DC/store lane model
margin_protected = suggested_qty × unit_cost × 0.35
net_benefit = margin_protected - transfer_cost
```

### 4.6 Inclusion gate

Include row only if:

- `suggested_qty > 0`
- `net_benefit > 0`

### 4.7 Recommendation label

| Condition | Label |
|-----------|-------|
| `net_benefit >= 25` | Transfer Recommended |
| else | Review Transfer |

Sort by Net Benefit descending.

---

## 5. Dashboard KPIs (Phase 1 ✅)

**Modules:** `kpi_service.py`, `kpi_dashboard_service.py`

| KPI | Inclusion logic |
|-----|-----------------|
| Total Inventory Value | Sum all Master `total_value` |
| Aged Inventory Value | Sum value where `age_days > 180` |
| Excess Inventory Value | Sum value where status ∈ {Excess, Excess / Aged} |
| Slow-Moving / Obsolete counts | COUNTIF status |
| Transfer candidates | COUNTIF action ∈ {Review Transfer, Transfer or Markdown} |
| Markdown candidates | COUNTIF action ∈ {Markdown Review, Transfer or Markdown, Liquidate} |
| Stockout Risk count | COUNTIF status |
| Estimated Recovery Value | Sum value for markdown candidate actions |
| Average Gross Margin % | AVERAGE gross margin column |

Chart aggregations use `kpi_dashboard_service` groupbys (location, status, aging buckets, actions, top excess).

---

## 6. Management Summary (Phase 1 ✅)

**Module:** `summary_service.py`

- KPI row: subset of dashboard (5 metrics via `management_summary_kpis`).
- Top risks: first 5 rows from aged/excess analysis (High/Medium).
- Action summary: value counts of `recommended_action` on full inventory.

---

## 7. Planned Rules — Inventory Classification (Prompt 04)

| Rule | Definition |
|------|------------|
| Annual usage value | `demand_90_day × 4 × unit_cost` (proxy) |
| ABC — A | Top SKUs until cumulative usage ≥ 80% |
| ABC — B | Next until cumulative ≥ 95% |
| ABC — C | Remainder |
| XYZ — X | CV(demand) < 0.5 |
| XYZ — Y | 0.5 ≤ CV < 1.0 |
| XYZ — Z | CV ≥ 1.0 |

---

## 8. Planned Rules — Cycle Count Plan (Prompt 05)

| Priority | Factor |
|----------|--------|
| 1 | ABC class (A before B before C) |
| 2 | Risk level from aged/excess logic |
| 3 | Days since last count > 90 |
| 4 | Inventory value descending |

---

## 9. Planned Rules — Replenishment (Prompt 06)

| Parameter | MVP formula |
|-----------|-------------|
| Avg daily demand | `demand_90_day / 90` |
| Safety stock | `1.65 × avg_daily_demand × √lead_time_days` (default z=1.65) |
| Reorder point | `avg_daily_demand × lead_time_days + safety_stock` |
| EOQ | `√(2 × annual_demand × order_cost / holding_cost)` |
| Projected stockout | Date when `on_hand - daily_demand × days <= 0` |
| Suggested order | When `on_hand <= reorder_point`, order max(EOQ, min_stock + demand - on_hand) |

Default lead time: 14 days (configurable). Holding cost: 25% of unit cost annually.

---

## 10. Planned Rules — Service Level & PO (Prompt 08)

| Metric | Rule |
|--------|------|
| Target service level | 95% default; 99% for A-class SKUs |
| Actual fill rate | `fulfilled_qty / demanded_qty` over 90 days |
| PO status | Open if `received_qty < order_qty`; Late if past expected receipt |
| Stockout events | Count days `quantity_on_hand < min_stock` |

---

## 11. Planned Rules — Vendor Scorecards (Prompt 09)

Weighted score (0–100):

```text
score = 0.35 × on_time_pct + 0.30 × fill_rate_pct + 0.20 × quality_pct + 0.15 × (100 - late_penalty)
```

| Tier | Score |
|------|-------|
| Preferred | ≥ 90 |
| Approved | 75–89 |
| Probation | 60–74 |
| Review | < 60 |

---

## 12. Rule Change Process

1. Update threshold in `config/workbook_config.py`.
2. Implement logic in appropriate `src/services/` module.
3. Adjust tests and regenerate golden expectations if needed.
4. Update this document and `DATA_DICTIONARY.md`.

---

## Related Documents

- [DATA_DICTIONARY.md](DATA_DICTIONARY.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [../prd.md](../prd.md)
