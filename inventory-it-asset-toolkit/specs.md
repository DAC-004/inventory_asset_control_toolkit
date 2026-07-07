# specs.md

# Inventory & IT Asset Control Toolkit — Technical Specification

## 1. Technical Overview

This project generates a professional Excel workbook called:

```text
Inventory_IT_Asset_Control_Toolkit.xlsx
```

The workbook is generated using Python and `openpyxl`.

The architecture should be simple, modular, reproducible, and easy to extend.

The workbook must be generated from source code, not manually created.

---

## 2. Recommended Tech Stack

### Language

```text
Python 3.11+
```

### Required Libraries

```text
openpyxl
pandas
numpy
faker
python-dateutil
```

### Optional Libraries

```text
pytest
black
ruff
mypy
```

---

## 3. Project Structure

Use the following structure:

```text
inventory-it-asset-toolkit/
│
├── README.md
├── PRD.md
├── specs.md
├── requirements.txt
├── .gitignore
│
├── config/
│   ├── workbook_config.py
│   └── style_config.py
│
├── data/
│   ├── generated/
│   │   ├── inventory_data.csv
│   │   ├── it_asset_data.csv
│   │   ├── software_license_data.csv
│   │   ├── mobile_data.csv
│   │   └── disposal_data.csv
│
├── dist/
│   └── Inventory_IT_Asset_Control_Toolkit.xlsx
│
├── src/
│   ├── main.py
│   ├── data_generation/
│   │   ├── generate_inventory.py
│   │   ├── generate_it_assets.py
│   │   ├── generate_software.py
│   │   ├── generate_mobile.py
│   │   └── generate_disposal.py
│   │
│   ├── workbook/
│   │   ├── builder.py
│   │   ├── styles.py
│   │   ├── formulas.py
│   │   ├── charts.py
│   │   ├── validations.py
│   │   └── utils.py
│   │
│   ├── sheets/
│   │   ├── readme_sheet.py
│   │   ├── master_inventory_sheet.py
│   │   ├── inventory_dashboard_sheet.py
│   │   ├── aged_excess_sheet.py
│   │   ├── markdown_planner_sheet.py
│   │   ├── transfer_planner_sheet.py
│   │   ├── it_asset_register_sheet.py
│   │   ├── audit_reconciliation_sheet.py
│   │   ├── software_licenses_sheet.py
│   │   ├── mobile_provisioning_sheet.py
│   │   ├── disposal_log_sheet.py
│   │   └── management_summary_sheet.py
│   │
│   └── tests/
│       ├── test_data_generation.py
│       ├── test_workbook_build.py
│       └── test_required_sheets.py
```

---

## 4. Architecture Principles

The build should follow these principles:

1. **Data generation is separate from workbook creation.**
2. **Business rules are centralized and reusable.**
3. **Styles are centralized.**
4. **Each worksheet has its own builder module.**
5. **The workbook can be regenerated with one command.**
6. **No macros or VBA.**
7. **All data is fictional and deterministic.**
8. **The output should be interview-ready without manual cleanup.**

---

## 5. Build Command

The project must generate the workbook with:

```bash
python src/main.py
```

Expected output:

```text
dist/Inventory_IT_Asset_Control_Toolkit.xlsx
```

---

## 6. Data Model

### 6.1 Inventory Record

```python
InventoryRecord = {
    "item_id": str,
    "sku": str,
    "product_name": str,
    "category": str,
    "subcategory": str,
    "location": str,
    "location_type": str,
    "region": str,
    "quantity_on_hand": int,
    "min_stock": int,
    "max_stock": int,
    "unit_cost": float,
    "selling_price": float,
    "total_value": float,
    "last_movement_date": date,
    "last_sale_date": date,
    "age_days": int,
    "demand_90_day": int,
    "sell_through_rate": float,
    "gross_margin_pct": float,
    "status": str,
    "recommended_action": str
}
```

---

### 6.2 IT Asset Record

```python
ITAssetRecord = {
    "asset_tag": str,
    "serial_number": str,
    "device_type": str,
    "make": str,
    "model": str,
    "assigned_user": str,
    "department": str,
    "location": str,
    "borough": str,
    "purchase_date": date,
    "warranty_expiration": date,
    "status": str,
    "condition": str,
    "last_audit_date": date,
    "lifecycle_stage": str,
    "notes": str
}
```

---

### 6.3 Software License Record

```python
SoftwareLicenseRecord = {
    "software_name": str,
    "vendor": str,
    "license_type": str,
    "purchased_licenses": int,
    "assigned_licenses": int,
    "available_licenses": int,
    "renewal_date": date,
    "days_until_renewal": int,
    "department": str,
    "owner": str,
    "annual_cost": float,
    "compliance_status": str
}
```

---

### 6.4 Mobile Provisioning Record

```python
MobileProvisioningRecord = {
    "employee_name": str,
    "department": str,
    "device_type": str,
    "asset_tag": str,
    "imei": str,
    "sim_number": str,
    "phone_number": str,
    "carrier": str,
    "mdm_enrolled": str,
    "security_configured": str,
    "required_apps_installed": str,
    "user_agreement_signed": str,
    "date_issued": date,
    "return_date": date | None,
    "status": str
}
```

---

### 6.5 Disposal Record

```python
DisposalRecord = {
    "asset_tag": str,
    "serial_number": str,
    "device_type": str,
    "assigned_user": str,
    "return_date": date,
    "condition": str,
    "data_wipe_required": str,
    "data_wipe_completed": str,
    "wipe_method": str,
    "disposal_vendor": str,
    "certificate_received": str,
    "disposal_date": date | None,
    "approved_by": str,
    "disposal_status": str
}
```

---

## 7. Business Rules

### 7.1 Inventory Status Rules

Apply these rules in order:

```text
IF quantity_on_hand < min_stock
    status = "Stockout Risk"
    recommended_action = "Replenish"

ELSE IF age_days > 365 AND demand_90_day = 0
    status = "Obsolete"
    recommended_action = "Liquidate"

ELSE IF quantity_on_hand > max_stock AND age_days > 180
    status = "Excess / Aged"
    recommended_action = "Transfer or Markdown"

ELSE IF quantity_on_hand > max_stock
    status = "Excess"
    recommended_action = "Review Transfer"

ELSE IF age_days > 180 AND sell_through_rate < 0.15
    status = "Slow-Moving"
    recommended_action = "Markdown Review"

ELSE
    status = "Healthy"
    recommended_action = "Monitor"
```

---

### 7.2 Markdown Rules

```text
IF age_days > 365 AND demand_90_day = 0
    suggested_markdown = 0.30
    disposition = "Liquidate"

ELSE IF age_days > 270
    suggested_markdown = 0.20
    disposition = "20% Markdown"

ELSE IF age_days > 180
    suggested_markdown = 0.10
    disposition = "10% Markdown"

ELSE
    suggested_markdown = 0.00
    disposition = "Hold"
```

---

### 7.3 Transfer Rules

Recommend transfer when:

```text
source_quantity > source_max_stock
destination_quantity < destination_min_stock
destination_demand > 0
net_benefit > 0
```

Suggested transfer quantity:

```text
MIN(
    source_quantity - source_max_stock,
    destination_min_stock - destination_quantity + destination_demand_buffer
)
```

Net benefit:

```text
estimated_margin_protected - transfer_cost
```

---

### 7.4 Software Compliance Rules

```text
IF assigned_licenses > purchased_licenses
    compliance_status = "Over-Assigned"

ELSE IF days_until_renewal <= 30
    compliance_status = "Renewal Due Soon"

ELSE IF days_until_renewal <= 90
    compliance_status = "Renewal Watch"

ELSE
    compliance_status = "Compliant"
```

---

### 7.5 Disposal Rules

```text
IF data_wipe_required = "Yes" AND data_wipe_completed = "No"
    disposal_status = "Pending Wipe"

ELSE IF data_wipe_completed = "Yes" AND certificate_received = "No"
    disposal_status = "Certificate Missing"

ELSE IF data_wipe_completed = "Yes" AND certificate_received = "Yes"
    disposal_status = "Disposed"

ELSE
    disposal_status = "Hold for Review"
```

---

## 8. Workbook Styling

### 8.1 Global Font

```text
Calibri or Aptos
```

### 8.2 Header Style

* Fill: Navy `#1F4E78`
* Font: White, bold
* Alignment: Center
* Border: Thin gray

### 8.3 KPI Card Style

* Fill: Light Blue `#D9EAF7`
* Title font: Dark Blue, bold
* Value font: Large, bold
* Border: Thin navy

### 8.4 Risk Colors

```text
Healthy / Compliant: Green
Watch / Renewal Watch: Yellow
Slow-Moving / Pending: Orange
Obsolete / Missing / Over-Assigned: Red
Neutral: Gray
```

---

## 9. Required Excel Features

The workbook must include:

* Filterable tables
* Frozen header rows
* Conditional formatting
* Data validation dropdowns
* KPI sections
* Charts
* Formulas
* Currency formatting
* Percentage formatting
* Date formatting
* Auto-width columns
* Print-ready management summary

---

## 10. Charts

Use openpyxl charts.

Required charts:

### Inventory Dashboard

* Bar chart: Inventory Value by Location
* Pie chart or doughnut-style equivalent: Inventory Status Breakdown
* Bar chart: Aging Bucket Summary
* Bar chart: Top 10 Excess Inventory Items

### Management Summary

* Recommended Action Summary
* Audit Exception Summary
* Software Compliance Summary

---

## 11. Workbook Sheet Order

The final sheet order must be:

```text
README
Master Inventory
Inventory Dashboard
Aged Excess Analysis
Markdown Planner
Transfer Planner
IT Asset Register
Audit Reconciliation
Software Licenses
Mobile Provisioning
Disposal Log
Management Summary
```

---

## 12. Sheet Naming Rules

Excel sheet names must be 31 characters or fewer.

Use exact sheet names listed in this spec.

---

## 13. Data Validation Dropdowns

Add dropdowns for:

### Inventory Status

```text
Healthy,Stockout Risk,Excess,Slow-Moving,Excess / Aged,Obsolete
```

### Recommended Action

```text
Monitor,Replenish,Review Transfer,Transfer or Markdown,Markdown Review,Liquidate
```

### IT Asset Status

```text
In Stock,Assigned,In Repair,Returned,Retired,Disposed,Missing
```

### Lifecycle Stage

```text
Received,Tagged,In Stock,Assigned,In Repair,Returned,Retired,Data Wiped,Disposed
```

### Compliance Status

```text
Compliant,Renewal Watch,Renewal Due Soon,Over-Assigned
```

### Disposal Status

```text
Pending Wipe,Wiped,Pending Vendor Pickup,Disposed,Certificate Missing,Hold for Review
```

---

## 14. README Sheet Content

The README sheet must contain:

* Toolkit name
* Version
* Author line
* Sample data disclaimer
* Purpose
* Mavis demo path
* IT Inventory demo path
* Key capabilities
* Notes for interview use

---

## 15. Management Summary Requirements

The Management Summary must fit on one printed page if possible.

It should include:

### Inventory Summary

* Total inventory value
* Aged inventory value
* Excess inventory value
* Transfer candidates
* Markdown candidates

### IT Asset Summary

* Total IT assets
* Assigned assets
* Missing assets
* Audit exceptions
* Assets pending disposal

### Software Summary

* Total software records
* Over-assigned licenses
* Renewals due within 90 days

### 30 / 60 / 90 Day Plan

30 days:

* Validate asset and inventory records
* Review high-risk exceptions
* Confirm current reporting needs

60 days:

* Standardize audit and reconciliation procedures
* Improve dashboard reporting
* Identify recurring inventory issues

90 days:

* Automate recurring reports
* Build KPI review cadence
* Recommend process improvements

---

## 16. Testing Requirements

Create tests that verify:

* Workbook file is created.
* Workbook contains all required sheets.
* Each required sheet has headers.
* Generated data has no duplicate primary keys.
* Inventory records include multiple statuses.
* IT asset records include multiple lifecycle stages.
* Software records include at least one over-assigned license.
* Disposal records include at least one pending wipe item.
* Workbook opens without corruption.

---

## 17. Error Handling

The build should:

* Create `dist/` if missing.
* Create `data/generated/` if missing.
* Fail gracefully with clear error messages.
* Not overwrite source files.
* Overwrite only generated outputs.
* Log successful workbook creation path.

---

## 18. README.md Requirements

The repository README must include:

* Project overview
* Screenshot placeholder
* Features
* Workbook tabs
* How to install
* How to run
* How to regenerate data
* Interview demo paths
* Future enhancements

---

## 19. Versioning

Initial version:

```text
v1.0.0
```

Include version on README sheet and repository README.

---

## 20. Acceptance Criteria

The build is complete when:

* `python src/main.py` creates the workbook.
* Workbook includes all required sheets.
* Workbook uses realistic fictional sample data.
* Workbook has professional styling.
* Dashboard KPIs calculate correctly.
* Required charts are present.
* Management Summary is printable.
* README explains how to demo the workbook.
* No real company data is used.
