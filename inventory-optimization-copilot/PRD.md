# Inventory Optimization Copilot — Product Requirements Document

**Version:** v2.0.0  
**Output:** `dist/Inventory_Optimization_Copilot.xlsx`

## 1. Product Name

**Inventory Optimization Copilot**

Decision-support for supply chain, procurement, warehouse, and distribution teams. The term *Copilot* refers to recommendations, prioritization, and management guidance — not a live AI model in the workbook.

## 2. Product Summary

A Python-generated Excel workbook demonstrating inventory health analysis, transfer and markdown planning, and executive reporting. All data is fictional and reproducible (seed `42`, as-of date `2026-07-01`).

## 3. Target Users

- Inventory / supply chain analysts
- Procurement and distribution managers
- Executive stakeholders reviewing inventory risk and recovery opportunity

## 4. Business Goals

1. Surface aged, excess, slow-moving, and obsolete inventory.
2. Recommend transfer before markdown when economically justified.
3. Model markdown and liquidation with margin awareness.
4. Provide leadership-ready dashboards and a printable management summary.

## 5. Workbook Tabs

### Phase 1 (this branch — prompt 01)

1. README  
2. Master Inventory  
3. Inventory Dashboard  
4. Aged Excess Analysis  
5. Markdown Planner  
6. Transfer Planner  
7. Management Summary  

### Target final order (prompts 04–09)

Insert between Transfer Planner and Management Summary:

- Inventory Classification  
- Cycle Count Plan  
- Replenishment Planning  
- Demand Forecast  
- Service Level Analysis  
- Purchase Order Tracker  
- Vendor Scorecards  

## 6. Explicitly Out of Scope

This product does **not** include:

- IT Asset Register  
- Audit Reconciliation  
- Software Licenses  
- Mobile Provisioning  
- Disposal Log  

Those capabilities belong to the future **IT Asset Control Toolkit** branch (`feature/it-asset-control-toolkit`).

## 7. Naming Policy

User-facing labels, documentation, demo scripts, screenshots, and workbook metadata must **not** contain the word `Mavis`.

## 8. Acceptance Criteria (phase 1)

1. Branch `feature/inventory-optimization-copilot` builds `Inventory_Optimization_Copilot.xlsx`.
2. Seven inventory tabs render in configured order.
3. No IT sheets or IT generators remain in this product tree.
4. `pytest` passes.
5. `python src/main.py` completes without error.
