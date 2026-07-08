# Inventory Optimization AI Co-Pilot

Enterprise Streamlit application for inventory health analytics, transfer optimization, markdown planning, and AI-assisted management summaries.

## Quick Start

```bash
cd apps/mavis_inventory_ai_copilot
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Run Tests

```bash
pytest
pytest --cov=src --cov-report=term-missing
ruff check .
```

## Demo Script

1. Launch the app with `streamlit run streamlit_app.py`
2. Start on **Executive Dashboard**
3. Explain total inventory value, aged inventory, excess exposure, and recovery opportunity
4. Open **Aged & Excess** to show exception prioritization
5. Open **Transfer Planner** to show network balancing
6. Open **Markdown Planner** to show margin-aware exit strategy
7. Open **AI Summary** to generate an executive-ready recommendation
8. Close by explaining real-world data integration opportunities

## Architecture

```
streamlit_app.py          # Streamlit entry point
src/config/             # Settings and constants
src/data/               # Loaders, validators, transformers
src/models/             # Pydantic data models
src/services/           # KPI, health, transfer, markdown, AI logic
src/ui/                 # Theme, components, pages
tests/                  # Unit, integration, and UI smoke tests
```

Business logic lives in `src/services/`. Streamlit pages call service functions only.

## Data Source

The app reads the Inventory IT Asset Control Toolkit workbook from `data/raw/` or falls back to the toolkit dist folder and `data/sample/sample_inventory.csv`. The source workbook is never modified.

## AI Summary

Set `AI_PROVIDER=local` in `.env` (default) for deterministic template-based summaries that require no API keys.
