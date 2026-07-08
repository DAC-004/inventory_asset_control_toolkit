"""Generate the complete interview demo script as a single DOCX file."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DOCX_PATH = DOCS / "Interview_Demo_Script.docx"


def _add_heading(doc: Document, text: str, level: int = 1) -> None:
    doc.add_heading(text, level=level)


def _add_bullet(doc: Document, text: str) -> None:
    doc.add_paragraph(text, style="List Bullet")


def _add_quote(doc: Document, text: str) -> None:
    p = doc.add_paragraph(text)
    p.paragraph_format.left_indent = Inches(0.25)
    for run in p.runs:
        run.italic = True


def _add_action(doc: Document, label: str, detail: str) -> None:
    p = doc.add_paragraph()
    p.add_run(f"{label}: ").bold = True
    p.add_run(detail)


def build_docx() -> Path:
    DOCS.mkdir(parents=True, exist_ok=True)
    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    title = doc.add_heading("Interview Demo Script", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sub = doc.add_paragraph("Inventory Optimization AI Co-Pilot")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].italic = True

    meta = doc.add_paragraph()
    meta.add_run("Duration: ").bold = True
    meta.add_run("~8–10 minutes\n")
    meta.add_run("Audience: ").bold = True
    meta.add_run("Supply chain leaders, analytics hiring panel\n")
    meta.add_run("Format: ").bold = True
    meta.add_run("Live Streamlit demo on Executive Dashboard with demo workbook loaded\n")
    meta.add_run("Data: ").bold = True
    meta.add_run("Fictional sample data from Inventory IT Asset Control Toolkit (read-only)")

    doc.add_paragraph()

    _add_heading(doc, "Pre-Demo Setup Checklist", level=1)
    for item in [
        "From repo root, confirm .env.local exists with OPENAI_API_KEY (gitignored — never commit).",
        "Optional: set AI_PROVIDER=openai and OPENAI_MODEL=gpt-4o-mini in .env.local.",
        "Install dependencies: cd apps/mavis_inventory_ai_copilot && pip install -r requirements.txt",
        "Start the app: streamlit run app.py (opens http://localhost:8501)",
        "Confirm sidebar shows data source, row count, and OpenAI mode when key is loaded.",
        "Land on Executive Dashboard before sharing screen.",
        "Have browser zoom at 100%; collapse unrelated tabs.",
        "If OpenAI fails during demo, switch AI Provider to local on the AI Summary page.",
    ]:
        _add_bullet(doc, item)

    _add_heading(doc, "Demo Flow", level=1)

    _add_heading(doc, "1. Opening (30 seconds)", level=2)
    _add_quote(
        doc,
        '"Retail inventory teams often have the data — but not a single place to turn it into action. '
        "Stores hold excess winter tires while another location is below minimum stock. Aged parts tie "
        'up cash. Markdown decisions get made in spreadsheets, if at all."',
    )
    _add_quote(
        doc,
        '"This co-pilot sits on top of our existing inventory toolkit and answers one question: '
        'where is money stuck, and what should we do next?"',
    )

    _add_heading(doc, "2. Hero Situation — Executive Dashboard (1 minute)", level=2)
    _add_action(doc, "Stay on Executive Dashboard", "Point to KPIs; do not read every number.")
    _add_quote(
        doc,
        '"Here\'s our network snapshot: total inventory value, SKU–location count, and exception '
        'signals across the network."',
    )
    doc.add_paragraph("The signals that matter:")
    for signal in [
        "Aged inventory value — cash sitting too long",
        "Excess exposure — above max stock",
        "Stockout risk count — service level at risk",
        "Estimated recovery — what markdown could return",
    ]:
        _add_bullet(doc, signal)
    _add_quote(
        doc,
        '"This is the control tower. Everything below is exception-driven — we don\'t ask analysts '
        'to scroll through healthy inventory."',
    )
    p = doc.add_paragraph(
        "Optional: Most value concentrates in a handful of locations; most risk is concentrated in "
        "excess/aged and slow-moving categories — that's where we drill next."
    )
    p.runs[0].italic = True

    _add_heading(doc, "3. Hero Product — Set the Story (20 seconds)", level=2)
    _add_action(doc, "Transition", "Before clicking Aged & Excess.")
    _add_quote(
        doc,
        '"Let me walk one product family through the full decision path: Mavis SnowTrack 205/55R16 — '
        "a winter tire with different health by location: obsolete at one DC, slow-moving at stores, "
        'stockout risk elsewhere. Same category, different actions."',
    )

    _add_heading(doc, "4. Aged & Excess Inventory (1.5 minutes)", level=2)
    _add_action(doc, "Navigate", "Sidebar → Aged & Excess")
    _add_quote(
        doc,
        '"This page shows exceptions only — not the full dataset. I\'ll filter to Issue Type = Obsolete / '
        "Excess / Aged / Slow-Moving and sort by inventory value so we work highest financial exposure "
        'first."',
    )
    doc.add_paragraph(
        "Hero SKU at DC-PA: high age, minimal demand — Obsolete, action Liquidate."
    )
    doc.add_paragraph(
        "At Store-Yonkers: same product line — Slow-Moving; aged but some demand remains."
    )
    _add_quote(
        doc,
        '"The app assigns risk level and recommended action with a plain-language reason on each row. '
        'Analysts use this as a prioritized work queue."',
    )
    _add_quote(
        doc,
        '"Every exception has an explanation — age, sell-through, min/max breach — so the '
        'recommendation is auditable, not a black box."',
    )

    _add_heading(doc, "5. Transfer Planner — First Action Path (1.5 minutes)", level=2)
    _add_action(doc, "Navigate", "Transfer Planner")
    _add_quote(doc, '"Before we markdown or liquidate, we ask: can the network absorb this inventory?"')
    doc.add_paragraph(
        "Transfer logic matches the same product across locations. Sources need excess above max stock; "
        "destinations need stock below minimum or low days of supply."
    )
    doc.add_paragraph(
        "Each recommendation shows suggested quantity, transfer cost, margin protected, and net benefit — "
        "ranked so ops sees the best moves first."
    )
    doc.add_paragraph(
        "For our hero tire family: DC with excess → store with stockout risk. We only recommend "
        "transfers where net benefit is positive."
    )
    _add_quote(
        doc,
        '"This is a rebalance, not a gut call: move X units, protect $Y margin, net $Z after transfer cost."',
    )

    _add_heading(doc, "6. Markdown Planner — Second Action Path (1.5 minutes)", level=2)
    _add_action(doc, "Navigate", "Markdown Planner")
    doc.add_paragraph(
        "When transfer isn't enough — or demand is fading — shift to margin-aware exit pricing."
    )
    doc.add_paragraph(
        "Markdown tiers follow business rules: deeper cuts for obsolete / 365+ day inventory; controlled "
        "markdowns for aged slow-movers with some sell-through."
    )
    doc.add_paragraph(
        "Each candidate shows current price, suggested markdown %, projected sell-through, estimated "
        "recovery value, and margin impact."
    )
    doc.add_paragraph(
        "Obsolete DC winter tire → Liquidate / aggressive markdown. Yonkers slow-mover → controlled markdown."
    )
    _add_quote(
        doc,
        '"Leadership can sort by recovery value to focus on the biggest cash-release opportunities this week."',
    )

    _add_heading(doc, "7. AI Management Summary (1.5 minutes)", level=2)
    _add_action(doc, "Navigate", "AI Summary → select OpenAI → click Generate Summary")
    _add_quote(
        doc,
        '"Analysts live in the tables; executives need a narrative. This summary is built from calculated '
        'KPIs and recommendations only — not invented SKUs or dollar amounts."',
    )
    doc.add_paragraph(
        "OpenAI generates the executive narrative from structured metrics sent to the API. Recommendation "
        "logic stays deterministic in the service layer — AI explains; it doesn't decide."
    )
    doc.add_paragraph(
        "Guardrails: mentions sample data basis, uses calculated KPIs only, and recommends human review "
        "before execution."
    )
    doc.add_paragraph(
        "Scroll the summary: references actual metrics and ends with next steps ops can approve. Use "
        "Download Summary (Markdown) if they ask for a handoff artifact."
    )
    p = doc.add_paragraph(
        "If API is unavailable: switch provider to local for a deterministic offline template, or confirm "
        "OPENAI_API_KEY in .env.local at repo root (gitignored)."
    )
    p.runs[0].italic = True

    _add_heading(doc, "8. Data Quality & Methodology (optional — 30 seconds if time)", level=2)
    _add_action(doc, "Navigate", "Data Quality → Methodology")
    doc.add_paragraph("Data Quality shows validation results and column coverage from the loaded workbook.")
    doc.add_paragraph(
        "Methodology documents classification rules, transfer/markdown thresholds, and AI guardrails."
    )
    doc.add_paragraph(
        "Use these if the panel asks how recommendations are derived or how we'd extend to live feeds."
    )

    _add_heading(doc, "9. Close (45 seconds)", level=2)
    doc.add_paragraph("Recap hero path: Dashboard → Aged & Excess → Transfer → Markdown → AI Summary")
    doc.add_paragraph(
        "Today reads from Inventory IT Asset Control Toolkit workbook — read-only. In production, same "
        "service layer connects to ERP, WMS, or POS feeds."
    )
    doc.add_paragraph(
        "56 automated tests cover KPIs, classification, transfers, markdowns, pipeline, and AI service."
    )
    _add_quote(
        doc,
        '"Happy to go deeper on architecture, business rules, or how we\'d wire this to live Mavis data."',
    )

    _add_heading(doc, "Quick Reference — Navigation Order", level=1)
    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "Step"
    hdr[1].text = "Page"
    hdr[2].text = "Key message"
    for step, page, msg in [
        ("1", "Executive Dashboard", "Where is money stuck?"),
        ("2", "Aged & Excess", "What to fix first?"),
        ("3", "Transfer Planner", "Move before you markdown."),
        ("4", "Markdown Planner", "Price the exit with margin guardrails."),
        ("5", "AI Summary", "OpenAI narrative from facts, not fiction."),
        ("6", "Data Quality / Methodology", "Optional — rules and validation if asked."),
    ]:
        row = table.add_row().cells
        row[0].text = step
        row[1].text = page
        row[2].text = msg

    _add_heading(doc, "Likely Interviewer Questions & Strong Answers", level=1)
    for question, answer in [
        (
            "How would you connect this to a live ERP or WMS?",
            "The structure mirrors production: a clean master dataset, calculated status fields, exception "
            "views, and a summary layer. Master Inventory maps to item/location tables; KPIs become SQL or BI "
            "measures; transfer and markdown logic stays in Python services. This app proves the logic — "
            "integration is the next step, not a different approach.",
        ),
        (
            "How do you decide transfer versus markdown?",
            "Transfer first when another location has demand and net benefit covers handling and freight. "
            "Markdown when age, demand, and sell-through show the item won't move at full price — or when "
            "holding cost exceeds recovery. The app encodes that sequence so the business doesn't jump to "
            "discounting inventory that could still be sold elsewhere.",
        ),
        (
            "Why not let AI make the recommendations?",
            "Decisions are rule-based, tested, and auditable. AI receives structured metrics only — KPIs, "
            "top risks, transfer and markdown summaries — and writes the executive narrative. It does not "
            "invent SKUs, values, or locations. Final approval stays with operations and merchandising.",
        ),
        (
            "What KPI would you watch most closely?",
            "Aged inventory value and markdown candidate count together. Aged dollars show tied-up cash; "
            "markdown candidates show how much is already flagged for action. If both rise while stockout "
            "risk also rises, replenishment and allocation — not just pricing — need attention.",
        ),
        (
            "Is this real data?",
            "No — all sample data is fictional and generated for demo purposes. Scenarios are realistic "
            "(excess at one location, stockout elsewhere, slow movers, obsolete items) but no real company "
            "information is included.",
        ),
        (
            "How is the AI summary secured?",
            "API keys live in .env.local at repo root (gitignored). Only aggregated metrics are sent to "
            "OpenAI — not raw row-level exports. Local provider works offline with no external calls.",
        ),
    ]:
        p = doc.add_paragraph()
        p.add_run(f"Q: {question}").bold = True
        doc.add_paragraph(answer)

    _add_heading(doc, "Delivery Tips", level=1)
    for tip in [
        "Don't read every KPI — pick 3–4 that tell the story.",
        "Use filters live — shows the app is interactive, not a static screenshot.",
        "Mention CSV/Markdown export if they ask about handoff to ops.",
        "If asked 'why not AI for everything?' — decisions are rule-based and tested; AI summarizes.",
        "If something looks empty — refresh data via sidebar Refresh Data.",
        "For OpenAI demo: wait for the spinner ('Calling OpenAI...') — confirms live API, not a template.",
    ]:
        _add_bullet(doc, tip)

    _add_heading(doc, "Technical Reference", level=1)
    for line in [
        "App entry: apps/mavis_inventory_ai_copilot/streamlit_app.py (streamlit run app.py)",
        "Data: data/raw/Inventory_IT_Asset_Control_Toolkit.xlsx with CSV fallback",
        "Secrets: .env.local at repo root or apps/mavis_inventory_ai_copilot/.env.local",
        "Tests: pytest from apps/mavis_inventory_ai_copilot (56 tests)",
        "Deploy: Static landing on Vercel; Streamlit runs locally or on internal host",
    ]:
        _add_bullet(doc, line)

    doc.add_paragraph()
    footer = doc.add_paragraph(
        "Generated by scripts/generate_demo_script_doc.py — regenerate after major app changes."
    )
    footer.runs[0].font.size = Pt(9)
    footer.runs[0].italic = True

    doc.save(DOCX_PATH)
    return DOCX_PATH


if __name__ == "__main__":
    path = build_docx()
    print(f"Complete demo script saved to: {path}")
