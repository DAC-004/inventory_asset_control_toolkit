# PRD.md

# Inventory & IT Asset Control Toolkit — Product Requirements Document

## 1. Product Name

**Inventory & IT Asset Control Toolkit**

## 2. Product Summary

The Inventory & IT Asset Control Toolkit is a professional Excel workbook generated through a Python-based build process. It is designed to showcase practical skills in inventory control, warehouse operations, IT asset lifecycle management, data analysis, audit reconciliation, reporting, and management-level decision support.

The workbook will support two interview use cases:

1. **Inventory Optimization / Supply Chain Analyst Use Case**

   * Focused on aged inventory, excess stock, transfer planning, markdown recommendations, inventory health, and KPI reporting.

2. **IT Inventory Control Specialist Use Case**

   * Focused on IT asset tracking, procurement intake, audits, software licenses, mobile provisioning, lifecycle management, disposal, and management reporting.

The toolkit must be clean, professional, ATS/interview-friendly, and suitable for an in-person laptop demo or printed portfolio.

---

## 3. Target Users

### Primary User

**Daniel A. Cruz**
Candidate demonstrating supply chain, inventory control, IT operations, ERP systems, reporting, and data analysis capabilities during interviews.

### Interview Audiences

#### Inventory Optimization Interview Audience

Hiring managers, procurement leaders, supply chain leaders, inventory managers, distribution leaders, and analytics stakeholders.

#### IT Inventory Control Interview Audience

IT managers, procurement staff, asset management teams, help desk leadership, compliance stakeholders, and operations leaders.

---

## 4. Business Goals

The toolkit should demonstrate the ability to:

* Maintain accurate inventory and asset records.
* Analyze inventory health across locations.
* Identify aged, excess, slow-moving, obsolete, and at-risk stock.
* Recommend business actions such as transfer, markdown, liquidation, disposal, or replenishment.
* Support warehouse and distribution decision-making.
* Track IT assets from receiving through assignment, audit, repair, return, data wipe, and disposal.
* Reconcile physical audits against system records.
* Track software licenses and renewal risks.
* Provide leadership-ready dashboards and summaries.
* Communicate complex operational data clearly.

---

## 5. Interview Story

The toolkit should support the following candidate narrative:

> “I built this toolkit to demonstrate how I approach inventory and asset control: clean data capture, lifecycle tracking, exception reporting, audit readiness, and management visibility. The same disciplined process applies whether I am analyzing warehouse inventory, retail stock, IT assets, software licenses, or equipment lifecycle status.”

---

## 6. Core Product Requirements

### 6.1 Workbook Format

The final deliverable must be an `.xlsx` workbook generated programmatically.

Required output:

```text
dist/Inventory_IT_Asset_Control_Toolkit.xlsx
```

The workbook must not require macros.

---

### 6.2 Workbook Tabs

The workbook must include the following tabs:

1. `README`
2. `Master Inventory`
3. `Inventory Dashboard`
4. `Aged Excess Analysis`
5. `Markdown Planner`
6. `Transfer Planner`
7. `IT Asset Register`
8. `Audit Reconciliation`
9. `Software Licenses`
10. `Mobile Provisioning`
11. `Disposal Log`
12. `Management Summary`

---

## 7. Sheet Requirements

### 7.1 README

Purpose:

Provide a clear guide for interviewers and reviewers.

Must include:

* Toolkit title
* Candidate value proposition
* Description of sample data
* Mavis / inventory optimization demo path
* IT inventory control demo path
* Notes that all data is fictional
* Workbook navigation guide

---

### 7.2 Master Inventory

Purpose:

Serve as the shared operational dataset for inventory and warehouse analysis.

Required fields:

* Item ID
* SKU
* Product Name
* Category
* Subcategory
* Location
* Location Type
* Region
* Quantity On Hand
* Min Stock
* Max Stock
* Unit Cost
* Selling Price
* Total Value
* Last Movement Date
* Last Sale Date
* Age Days
* 90 Day Demand
* Sell Through Rate
* Gross Margin %
* Status
* Recommended Action

Required logic:

* Total Value = Quantity On Hand × Unit Cost
* Gross Margin % = `(Selling Price - Unit Cost) / Selling Price`
* Age Days calculated from workbook run date or fixed demo date
* Status assigned based on inventory rules
* Recommended Action assigned based on inventory condition

---

### 7.3 Inventory Dashboard

Purpose:

Provide leadership-level visibility into inventory health.

Required KPIs:

* Total Inventory Value
* Aged Inventory Value
* Excess Inventory Value
* Slow-Moving SKU Count
* Obsolete SKU Count
* Transfer Candidate Count
* Markdown Candidate Count
* Stockout Risk Count
* Estimated Recovery Value
* Average Gross Margin %

Required charts:

* Inventory Value by Location
* Inventory Status Breakdown
* Aging Bucket Summary
* Recommended Action Summary
* Top 10 Excess Inventory Items

Design expectations:

* Executive dashboard look
* Clean color palette
* Large KPI cards
* Clear section titles
* No clutter

---

### 7.4 Aged Excess Analysis

Purpose:

Identify slow-moving, aged, excess, obsolete, and risky inventory.

Required fields:

* SKU
* Product Name
* Location
* Quantity On Hand
* Max Stock
* Excess Quantity
* Age Days
* 90 Day Demand
* Sell Through Rate
* Inventory Value
* Risk Level
* Issue Type
* Recommended Action
* Analyst Notes

Required rules:

* Quantity On Hand > Max Stock → Excess
* Age Days > 180 and Sell Through Rate < 15% → Slow-Moving
* Age Days > 365 and 90 Day Demand = 0 → Obsolete
* Quantity On Hand < Min Stock → Stockout Risk
* Excess at one location and shortage at another → Transfer Candidate
* Obsolete with no transfer demand → Markdown or Liquidation Candidate

---

### 7.5 Markdown Planner

Purpose:

Model markdown options for aged or end-of-life inventory.

Required fields:

* SKU
* Product Name
* Location
* Quantity On Hand
* Unit Cost
* Current Selling Price
* Current Margin %
* Age Days
* Demand Trend
* Suggested Markdown %
* Markdown Price
* Projected Sell Through %
* Estimated Recovery Value
* Margin Impact
* Recommended Disposition

Recommended dispositions:

* Hold
* Transfer First
* 10% Markdown
* 20% Markdown
* 30% Markdown
* Liquidate
* Discontinue
* Dispose

---

### 7.6 Transfer Planner

Purpose:

Recommend inventory transfers between locations to improve stock balance.

Required fields:

* SKU
* Product Name
* Source Location
* Destination Location
* Source Quantity
* Destination Quantity
* Destination Min Stock
* Destination Demand
* Suggested Transfer Quantity
* Unit Cost
* Transfer Cost
* Estimated Margin Protected
* Net Benefit
* Recommendation

Required logic:

Recommend transfer when:

* Source location has excess
* Destination location is below minimum or has strong demand
* Suggested transfer quantity is greater than zero
* Net benefit is positive

---

### 7.7 IT Asset Register

Purpose:

Track IT assets through their lifecycle.

Required fields:

* Asset Tag
* Serial Number
* Device Type
* Make
* Model
* Assigned User
* Department
* Location
* Borough
* Purchase Date
* Warranty Expiration
* Status
* Condition
* Last Audit Date
* Lifecycle Stage
* Notes

Lifecycle stages:

* Received
* Tagged
* In Stock
* Assigned
* In Repair
* Returned
* Retired
* Data Wiped
* Disposed

---

### 7.8 Audit Reconciliation

Purpose:

Compare system asset records against physical audit results.

Required sections:

1. System Inventory
2. Physical Audit Count
3. Exceptions Report

Required exception types:

* Missing from Audit
* Found Not in System
* Wrong Location
* Wrong User
* Duplicate Serial Number
* Missing Asset Tag
* Retired but Active
* No Exception

Required outputs:

* Total assets audited
* Exception count
* Exception rate
* High-priority exceptions
* Follow-up owner
* Resolution status

---

### 7.9 Software Licenses

Purpose:

Track software license usage, compliance, and renewal risk.

Required fields:

* Software Name
* Vendor
* License Type
* Purchased Licenses
* Assigned Licenses
* Available Licenses
* Renewal Date
* Days Until Renewal
* Department
* Owner
* Annual Cost
* Compliance Status

Required rules:

* Assigned Licenses > Purchased Licenses → Over-Assigned
* Renewal within 30 days → Renewal Due Soon
* Renewal within 90 days → Renewal Watch
* Assigned Licenses <= Purchased Licenses → Compliant

---

### 7.10 Mobile Provisioning

Purpose:

Standardize mobile phone provisioning and recovery.

Required fields:

* Employee Name
* Department
* Device Type
* Asset Tag
* IMEI
* SIM Number
* Phone Number
* Carrier
* MDM Enrolled
* Security Configured
* Required Apps Installed
* User Agreement Signed
* Date Issued
* Return Date
* Status

Required statuses:

* Ready
* Assigned
* Pending Setup
* Missing Agreement
* Returned
* Disabled

---

### 7.11 Disposal Log

Purpose:

Track asset retirement, data destruction, vendor disposal, and approval.

Required fields:

* Asset Tag
* Serial Number
* Device Type
* Assigned User
* Return Date
* Condition
* Data Wipe Required
* Data Wipe Completed
* Wipe Method
* Disposal Vendor
* Certificate Received
* Disposal Date
* Approved By
* Disposal Status

Required statuses:

* Pending Wipe
* Wiped
* Pending Vendor Pickup
* Disposed
* Certificate Missing
* Hold for Review

---

### 7.12 Management Summary

Purpose:

Provide a printable one-page executive summary.

Required sections:

* Inventory Health Highlights
* Top Risks
* Recommended Actions
* IT Asset Control Highlights
* Audit Exceptions
* Software License Risks
* Disposal / Lifecycle Risks
* 30 / 60 / 90 Day Action Plan

---

## 8. Sample Data Requirements

The workbook must use fictional sample data only.

Sample data must include:

### Inventory Data

* 80 to 150 inventory rows
* Multiple SKUs
* Multiple locations
* At least 3 DCs
* At least 8 stores
* Multiple regions
* Aged inventory examples
* Excess inventory examples
* Stockout examples
* Markdown candidates
* Transfer candidates

### IT Asset Data

* 80 to 150 IT asset rows
* Laptops
* Desktops
* Printers
* Scanners
* Mobile phones
* Monitors
* Network devices
* Assigned assets
* Missing assets
* Retired assets
* Assets pending disposal
* Assets with expiring warranties

### Software Data

* 15 to 30 software records
* Compliant licenses
* Over-assigned licenses
* Renewals due in 30 / 60 / 90 days

---

## 9. Design Requirements

The workbook must look professional and interview-ready.

Required design standards:

* Consistent theme colors
* Dark header rows with white text
* Frozen top rows
* Filterable Excel tables
* Auto-sized columns
* Currency and percentage formatting
* Conditional formatting for risks
* KPI cards on dashboards
* Clear section labels
* Print-friendly management summary
* No unnecessary decoration
* No macros

Suggested color palette:

* Navy: `#1F4E78`
* Dark Blue: `#17365D`
* Light Blue: `#D9EAF7`
* Green: `#70AD47`
* Yellow: `#FFC000`
* Orange: `#ED7D31`
* Red: `#C00000`
* Gray: `#F2F2F2`
* White: `#FFFFFF`

---

## 10. Success Criteria

The workbook is successful when:

* It opens cleanly in Microsoft Excel.
* All required tabs are present.
* All tables have realistic fictional data.
* Dashboards are readable and professional.
* Formulas work correctly.
* Conditional formatting highlights risks.
* Management Summary is printable.
* The workbook supports a 3-minute Mavis demo.
* The workbook supports a 3-minute IT Inventory Control demo.
* The project can be regenerated from source code.

---

## 11. Demo Scripts

### Mavis / Inventory Optimization Demo

> “This section of the toolkit focuses on inventory optimization. The dashboard shows inventory value, aged stock, excess inventory, transfer candidates, markdown candidates, and estimated recovery value. From there, I can drill into aged and excess inventory, evaluate whether a transfer should happen before markdown, and use the markdown planner to protect margin while exiting slow-moving inventory.”

Recommended demo path:

1. Inventory Dashboard
2. Aged Excess Analysis
3. Transfer Planner
4. Markdown Planner
5. Management Summary

---

### IT Inventory Control Demo

> “This section focuses on IT asset lifecycle control. The asset register tracks equipment from receipt through assignment, audit, return, repair, data wipe, and disposal. The audit reconciliation tab compares system inventory against physical audit results and flags exceptions. The license tracker and mobile provisioning tabs help standardize compliance and equipment control.”

Recommended demo path:

1. IT Asset Register
2. Audit Reconciliation
3. Software Licenses
4. Mobile Provisioning
5. Disposal Log
6. Management Summary

---

## 12. Out of Scope

The first version will not include:

* Live ERP integration
* Live API connections
* Macros
* VBA
* Real company data
* Authentication
* Cloud deployment
* Real AI integration
* Barcode scanning

These can be considered future enhancements.

---

## 13. Future Enhancements

Possible future enhancements:

* Power BI version
* Streamlit dashboard
* Next.js AI inventory app
* Barcode scan import
* ERP export/import templates
* ServiceNow or Zoho asset import template
* AI-generated management summary
* Automated PDF report export
* SQL database backend
* Role-based access controls
