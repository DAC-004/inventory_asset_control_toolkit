cursor_prompts.md
Cursor Prompt Pack — Inventory & IT Asset Control Toolkit
Use these prompts in Cursor step by step. Paste one prompt at a time.
________________________________________
Prompt 1 — Create Project Scaffold
You are a senior Python developer, supply chain data analyst, warehouse inventory analyst, and Excel automation expert.

Create a clean Python project that generates a professional Excel workbook called Inventory_IT_Asset_Control_Toolkit.xlsx.

Use this structure:

inventory-it-asset-toolkit/
├── README.md
├── PRD.md
├── specs.md
├── requirements.txt
├── .gitignore
├── config/
│   ├── workbook_config.py
│   └── style_config.py
├── data/
│   └── generated/
├── dist/
├── src/
│   ├── main.py
│   ├── data_generation/
│   ├── workbook/
│   ├── sheets/
│   └── tests/

Use Python 3.11+.

The workbook will be generated using openpyxl, pandas, numpy, faker, and python-dateutil.

Create all directories and placeholder files. Add clean docstrings and comments. Do not create unnecessary complexity.
________________________________________
Prompt 2 — Add Requirements and Config
Add requirements.txt with:

openpyxl
pandas
numpy
faker
python-dateutil
pytest
black
ruff

Create config/workbook_config.py and config/style_config.py.

workbook_config.py should define:
- workbook title
- version
- output filename
- required sheet order
- demo date
- row counts for generated sample data
- inventory thresholds
- markdown thresholds
- software renewal thresholds

style_config.py should define:
- colors
- fonts
- header styles
- KPI card styles
- risk color mappings
- currency, percentage, date, and integer number formats

Keep config clean, readable, and easy to modify.
________________________________________
Prompt 3 — Generate Inventory Sample Data
Build src/data_generation/generate_inventory.py.

Create a function generate_inventory_data(row_count: int, seed: int) -> pandas.DataFrame.

The data must be fictional and realistic for an inventory optimization interview.

Include these columns:
- Item ID
- SKU
- Product Name
- Category
- Subcategory
- Location
- Location Type
- Region
- Quantity On Hand
- Min Stock
- Max Stock
- Unit Cost
- Selling Price
- Total Value
- Last Movement Date
- Last Sale Date
- Age Days
- 90 Day Demand
- Sell Through Rate
- Gross Margin %
- Status
- Recommended Action

Use sample categories such as tires, brake parts, batteries, filters, fluids, tools, shop supplies, and accessories.

Use locations such as DC-NY, DC-NJ, DC-PA, Store-Bronx, Store-Queens, Store-Brooklyn, Store-Manhattan, Store-WhitePlains, Store-Yonkers, Store-Newark, Store-Stamford.

Create business rules:
- Stockout Risk when Quantity On Hand < Min Stock
- Obsolete when Age Days > 365 and 90 Day Demand = 0
- Excess / Aged when Quantity On Hand > Max Stock and Age Days > 180
- Excess when Quantity On Hand > Max Stock
- Slow-Moving when Age Days > 180 and Sell Through Rate < 15%
- Healthy otherwise

Recommended Action:
- Replenish
- Liquidate
- Transfer or Markdown
- Review Transfer
- Markdown Review
- Monitor

Make sure the dataset includes examples of every status.
Save generated CSV to data/generated/inventory_data.csv.
________________________________________
Prompt 4 — Generate IT Asset, Software, Mobile, and Disposal Data
Create these files:

src/data_generation/generate_it_assets.py
src/data_generation/generate_software.py
src/data_generation/generate_mobile.py
src/data_generation/generate_disposal.py

Each file should expose a generate_* function returning a pandas DataFrame and also save a CSV into data/generated/.

IT asset data columns:
- Asset Tag
- Serial Number
- Device Type
- Make
- Model
- Assigned User
- Department
- Location
- Borough
- Purchase Date
- Warranty Expiration
- Status
- Condition
- Last Audit Date
- Lifecycle Stage
- Notes

Software license data columns:
- Software Name
- Vendor
- License Type
- Purchased Licenses
- Assigned Licenses
- Available Licenses
- Renewal Date
- Days Until Renewal
- Department
- Owner
- Annual Cost
- Compliance Status

Mobile provisioning data columns:
- Employee Name
- Department
- Device Type
- Asset Tag
- IMEI
- SIM Number
- Phone Number
- Carrier
- MDM Enrolled
- Security Configured
- Required Apps Installed
- User Agreement Signed
- Date Issued
- Return Date
- Status

Disposal data columns:
- Asset Tag
- Serial Number
- Device Type
- Assigned User
- Return Date
- Condition
- Data Wipe Required
- Data Wipe Completed
- Wipe Method
- Disposal Vendor
- Certificate Received
- Disposal Date
- Approved By
- Disposal Status

Ensure sample data includes:
- assigned assets
- in-stock assets
- missing assets
- retired assets
- pending disposal assets
- over-assigned software licenses
- renewals due in 30, 60, and 90 days
- mobile devices pending setup
- disposal records pending wipe
- records missing disposal certificates
________________________________________
Prompt 5 — Create Workbook Builder and Styling Utilities
Create workbook utilities:

src/workbook/builder.py
src/workbook/styles.py
src/workbook/utils.py
src/workbook/formulas.py
src/workbook/charts.py
src/workbook/validations.py

builder.py:
- create a new openpyxl Workbook
- remove the default sheet
- call each worksheet builder in the required order
- save to dist/Inventory_IT_Asset_Control_Toolkit.xlsx

styles.py:
- functions for title style
- section header style
- table header style
- KPI card style
- risk conditional formatting
- borders
- alignment
- freeze panes

utils.py:
- autosize columns
- create Excel table
- apply filters
- format currency columns
- format percentage columns
- format date columns
- set print layout

validations.py:
- functions to add dropdown validations for statuses, lifecycle stages, compliance statuses, and disposal statuses

charts.py:
- helper functions for bar charts and pie charts using openpyxl

Keep each helper modular and reusable.
________________________________________
Prompt 6 — Build README Sheet
Create src/sheets/readme_sheet.py.

Build a professional README worksheet for the Excel workbook.

Include:
- Toolkit title
- Version
- Author: Daniel A. Cruz
- Disclaimer: all data is fictional sample data
- Purpose of the workbook
- Mavis / Inventory Optimization demo path
- IT Inventory Control demo path
- Key capabilities
- Recommended interview talking points

Apply professional formatting:
- title area
- shaded section headers
- readable row spacing
- wrapped text
- clean column widths
________________________________________
Prompt 7 — Build Master Inventory Sheet
Create src/sheets/master_inventory_sheet.py.

Build the Master Inventory sheet from inventory_data DataFrame.

Requirements:
- Add title
- Add data table
- Freeze header row
- Apply filters
- Apply Excel table formatting
- Format currency, percentages, dates, and integers
- Add conditional formatting for Status and Recommended Action
- Add dropdowns to Status and Recommended Action columns
- Autosize columns

This sheet must look like a professional analyst workbook, not raw exported data.
________________________________________
Prompt 8 — Build Inventory Dashboard
Create src/sheets/inventory_dashboard_sheet.py.

Build an executive dashboard from inventory_data.

Required KPI cards:
- Total Inventory Value
- Aged Inventory Value
- Excess Inventory Value
- Slow-Moving SKU Count
- Obsolete SKU Count
- Transfer Candidate Count
- Markdown Candidate Count
- Stockout Risk Count
- Estimated Recovery Value
- Average Gross Margin %

Create summary tables for:
- Inventory Value by Location
- Inventory Status Breakdown
- Aging Bucket Summary
- Recommended Action Summary
- Top 10 Excess Inventory Items

Create charts:
- bar chart for Inventory Value by Location
- pie chart for Inventory Status Breakdown
- bar chart for Aging Bucket Summary
- bar chart for Top 10 Excess Inventory Items

Use professional dashboard formatting:
- KPI cards at top
- charts below
- clean spacing
- navy/blue/gray theme
- freeze panes not required
- hide gridlines
________________________________________
Prompt 9 — Build Aged Excess Analysis Sheet
Create src/sheets/aged_excess_sheet.py.

Build the Aged Excess Analysis sheet from inventory_data.

Include columns:
- SKU
- Product Name
- Location
- Quantity On Hand
- Max Stock
- Excess Quantity
- Age Days
- 90 Day Demand
- Sell Through Rate
- Inventory Value
- Risk Level
- Issue Type
- Recommended Action
- Analyst Notes

Calculate:
- Excess Quantity = max(Quantity On Hand - Max Stock, 0)
- Risk Level:
  - High for Obsolete, Excess / Aged, Stockout Risk
  - Medium for Excess or Slow-Moving
  - Low for Healthy
- Issue Type based on status
- Analyst Notes with short business-readable comments

Apply conditional formatting:
- High risk red
- Medium risk orange/yellow
- Low risk green

Add filters and table formatting.
________________________________________
Prompt 10 — Build Markdown Planner
Create src/sheets/markdown_planner_sheet.py.

Build the Markdown Planner from inventory records where status is Slow-Moving, Excess / Aged, Obsolete, or Excess.

Include columns:
- SKU
- Product Name
- Location
- Quantity On Hand
- Unit Cost
- Current Selling Price
- Current Margin %
- Age Days
- Demand Trend
- Suggested Markdown %
- Markdown Price
- Projected Sell Through %
- Estimated Recovery Value
- Margin Impact
- Recommended Disposition

Use rules:
- Age > 365 and demand = 0: 30% markdown / Liquidate
- Age > 270: 20% markdown
- Age > 180: 10% markdown
- Otherwise: Hold or Transfer First

Calculate:
- Markdown Price
- Estimated Recovery Value
- Margin Impact

Apply currency and percentage formats.
Add conditional formatting for Recommended Disposition.
________________________________________
Prompt 11 — Build Transfer Planner
Create src/sheets/transfer_planner_sheet.py.

Build a Transfer Planner using inventory_data.

Identify possible transfers where:
- one location has Quantity On Hand > Max Stock for a SKU or category
- another location has Quantity On Hand < Min Stock or strong demand
- source and destination are not the same
- net benefit is positive

Include columns:
- SKU
- Product Name
- Source Location
- Destination Location
- Source Quantity
- Destination Quantity
- Destination Min Stock
- Destination Demand
- Suggested Transfer Quantity
- Unit Cost
- Transfer Cost
- Estimated Margin Protected
- Net Benefit
- Recommendation

Create realistic transfer cost estimates.
Use a simple net benefit model:
Estimated Margin Protected = Suggested Transfer Quantity * Unit Cost * 0.35
Net Benefit = Estimated Margin Protected - Transfer Cost

Add conditional formatting:
- positive net benefit green
- negative or zero red
- transfer recommended green
________________________________________
Prompt 12 — Build IT Asset Register
Create src/sheets/it_asset_register_sheet.py.

Build the IT Asset Register from it_asset_data.

Requirements:
- Title
- Filterable table
- Frozen header row
- Conditional formatting for Status and Lifecycle Stage
- Date formatting
- Dropdowns for Status and Lifecycle Stage
- Highlight warranty expirations within 90 days
- Highlight missing assets in red
- Autosize columns

This sheet should look ready for an IT asset management interview.
________________________________________
Prompt 13 — Build Audit Reconciliation Sheet
Create src/sheets/audit_reconciliation_sheet.py.

Build an Audit Reconciliation sheet.

Create:
1. Summary KPI section
2. System Inventory sample table
3. Physical Audit sample table
4. Exceptions Report

Generate exceptions from the IT asset data:
- Missing from Audit
- Found Not in System
- Wrong Location
- Wrong User
- Duplicate Serial Number
- Missing Asset Tag
- Retired but Active
- No Exception

Include columns:
- Asset Tag
- Serial Number
- Expected Location
- Actual Location
- Expected User
- Actual User
- Exception Type
- Priority
- Follow-Up Owner
- Resolution Status

Add conditional formatting:
- high priority red
- medium orange
- no exception green

Add summary counts by exception type.
________________________________________
Prompt 14 — Build Software Licenses Sheet
Create src/sheets/software_licenses_sheet.py.

Build the Software Licenses sheet from software_license_data.

Requirements:
- Filterable table
- Conditional formatting for Compliance Status
- Highlight Over-Assigned in red
- Highlight Renewal Due Soon in orange
- Highlight Renewal Watch in yellow
- Currency formatting for Annual Cost
- Date formatting for Renewal Date
- Integer formatting for license counts

Add a small summary section:
- Total software records
- Over-assigned count
- Renewals due within 30 days
- Renewals due within 90 days
- Total annual cost
________________________________________
Prompt 15 — Build Mobile Provisioning Sheet
Create src/sheets/mobile_provisioning_sheet.py.

Build the Mobile Provisioning sheet from mobile_data.

Requirements:
- Filterable table
- Conditional formatting for Status
- Highlight Pending Setup and Missing Agreement
- Dropdowns for Yes/No fields
- Dropdowns for Status
- Date formatting
- Autosize columns

Add a checklist-style summary at the top:
- Total mobile devices
- Assigned devices
- Pending setup
- Missing user agreement
- Returned devices
________________________________________
Prompt 16 — Build Disposal Log Sheet
Create src/sheets/disposal_log_sheet.py.

Build the Disposal Log from disposal_data.

Requirements:
- Filterable table
- Conditional formatting for Disposal Status
- Highlight Pending Wipe
- Highlight Certificate Missing
- Highlight Disposed
- Date formatting
- Yes/No dropdowns
- Disposal Status dropdown
- Autosize columns

Add a summary section:
- Total disposal records
- Pending wipe
- Certificate missing
- Disposed
- Hold for review
________________________________________
Prompt 17 — Build Management Summary Sheet
Create src/sheets/management_summary_sheet.py.

Build a printable one-page Management Summary.

Include these sections:

1. Inventory Health Highlights
- Total inventory value
- Aged inventory value
- Excess inventory value
- Transfer candidates
- Markdown candidates

2. IT Asset Control Highlights
- Total IT assets
- Assigned assets
- Missing assets
- Audit exceptions
- Assets pending disposal

3. Software License Risks
- Over-assigned licenses
- Renewals due within 90 days
- Total annual software cost

4. Top Risks
- Top 5 inventory risks
- Top 5 IT asset risks

5. 30 / 60 / 90 Day Action Plan

Format as a professional executive one-pager:
- hide gridlines
- print landscape
- fit to one page wide
- clear section headers
- KPI cards
________________________________________
Prompt 18 — Wire Everything in main.py
Update src/main.py so running:

python src/main.py

does the following:
1. Creates required folders if missing
2. Generates all fictional sample data
3. Saves generated CSV files to data/generated/
4. Builds the Excel workbook
5. Saves workbook to dist/Inventory_IT_Asset_Control_Toolkit.xlsx
6. Prints a success message with the output path

Add basic error handling and clear console messages.
________________________________________
Prompt 19 — Add Tests
Create pytest tests.

Tests should verify:
- generated inventory data is not empty
- generated IT asset data is not empty
- inventory data includes all required columns
- IT asset data includes all required columns
- software data includes at least one Over-Assigned record
- workbook file is created
- workbook contains all required sheet names
- required sheets are in the correct order
- workbook can be opened with openpyxl

Keep tests practical and not overly complex.
________________________________________
Prompt 20 — Add README.md
Create a professional README.md for the project.

Include:
- project title
- overview
- features
- workbook tabs
- tech stack
- installation steps
- run command
- output location
- demo path for inventory optimization interview
- demo path for IT inventory control interview
- sample data disclaimer
- future enhancements

Make it polished enough to show in GitHub or Cursor during an interview.
________________________________________
Prompt 21 — Final Polish Pass
Perform a final polish pass on the entire project.

Check:
- code organization
- imports
- naming consistency
- formatting
- workbook styling
- dashboard readability
- formulas
- output path
- tests
- README
- no real company data
- all data is fictional
- all required tabs exist
- workbook opens correctly

Improve anything that looks rough or unprofessional.

Do not add unnecessary features. Keep the architecture concise, organized, and interview-ready.
________________________________________
Prompt 22 — Interview Demo Script File
Create docs/demo_script.md.

Include two 3-minute demo scripts:

1. Mavis Inventory Optimization demo
2. IT Inventory Control Specialist demo

Each script should include:
- opening statement
- tabs to show
- what to say on each tab
- closing statement
- likely interviewer questions
- strong answers

Keep the language natural and professional.
________________________________________
Prompt 23 — Architecture Summary File
Create docs/architecture.md.

Document the architecture in a concise way:
- purpose
- project structure
- data generation layer
- workbook generation layer
- worksheet modules
- styling layer
- testing layer
- how to extend the project
- future path toward a web app or AI assistant

Keep it clear enough for a hiring manager and technical enough for an IT/data interviewer.
________________________________________
Prompt 24 — Create One Command Build Script
Add a simple build script.

For Windows:
create build.bat that runs:
python src/main.py

For Mac/Linux:
create build.sh that runs:
python src/main.py

Update README.md to mention these scripts.

Make sure the scripts are simple and safe.
________________________________________
Prompt 25 — Final Cursor Instruction
Review PRD.md and specs.md.

Compare the current implementation against every requirement.

Create a checklist of completed items and missing items.

Fix missing requirements.

Then run the project and confirm the workbook is generated successfully.

Do not stop until the workbook builds and all required sheets are present.
