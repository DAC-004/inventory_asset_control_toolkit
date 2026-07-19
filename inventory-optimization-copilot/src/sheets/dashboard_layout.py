"""Deterministic Inventory Dashboard layout specification (canvas A:V)."""

from __future__ import annotations

from dataclasses import dataclass

DASHBOARD_CANVAS_COLS = 22  # A through V
TABLE_AREA_END_COL = 8  # A:H
DIVIDER_COL = 9  # I spacer
CHART_AREA_START_COL = 10  # J
CHART_AREA_END_COL = 22  # V
CHART_ANCHOR_COL = "J"
CHART_LABEL_COL = 8  # column H — chart category helper outside table range

KPI_START_ROW = 1
KPI_END_ROW = 8
FREEZE_PANE = "A9"
SECTIONS_START_ROW = 10
SECTION_SPACER_ROWS = 2
CHART_BOTTOM_MARGIN_ROWS = 2

CHART_WIDTH_CM = 26.0
CHART_HEIGHT_CM = 11.5
CHART_MIN_WIDTH_CM = 22.0
CHART_MAX_WIDTH_CM = 28.0
CHART_MIN_HEIGHT_CM = 8.0
CHART_MAX_HEIGHT_CM = 12.5
CHART_ROW_CM = 0.45
CHART_CM_PER_EXCEL_ROW = 0.40
MIN_CHART_BODY_ROWS = 10

AS_OF_CONTEXT = "As of July 1, 2026"

DASHBOARD_COLUMN_WIDTHS: dict[str, float] = {
    "A": 20,
    "B": 22,
    "C": 16,
    "D": 16,
    "E": 16,
    "F": 16,
    "G": 16,
    "H": 16,
    "I": 3,
    "J": 12,
    "K": 12,
    "L": 12,
    "M": 12,
    "N": 12,
    "O": 12,
    "P": 12,
    "Q": 12,
    "R": 12,
    "S": 12,
    "T": 12,
    "U": 12,
    "V": 12,
}

SECTION_TITLE_HEIGHT = 28
TABLE_HEADER_HEIGHT = 32
DATA_ROW_HEIGHT = 22
CONTEXT_ROW_HEIGHT = 16

CHART_TITLES: dict[str, str] = {
    "location": "Inventory Value by Location",
    "status": "Inventory Exposure by Status",
    "aging": "Inventory Value by Aging Bucket",
    "top_excess": "Top 10 Excess Inventory Items",
    "abc_usage": "Annual Usage Value by ABC Class",
    "replenishment": "Replenishment Requirements by Status",
    "fill_rate": "Fill Rate by Location",
    "vendor_risk": "Supplier Exposure by Risk Class",
    "transfer_benefit": "Top Transfer Opportunities by Net Benefit",
    "action": "Inventory Value by Recommended Action",
}

CHART_SERIES_NAMES: dict[str, str] = {
    "location": "Inventory Value",
    "status": "Inventory Value",
    "aging": "Inventory Value",
    "top_excess": "Excess Inventory Value",
    "abc_usage": "Annual Usage Value",
    "replenishment": "Recommended Order Value",
    "vendor_risk": "Open PO Value",
    "transfer_benefit": "Net Benefit",
    "action": "Inventory Value",
}


@dataclass(frozen=True)
class DashboardSectionDef:
    """Logical dashboard section — row span computed at build time."""

    key: str
    title: str
    chart_type: str
    ranked: bool = False
    context: str = AS_OF_CONTEXT


@dataclass
class DashboardSectionLayout:
    """Resolved row block for one table/chart pair."""

    key: str
    title: str
    chart_title: str
    chart_type: str
    start_row: int
    end_row: int
    context: str = AS_OF_CONTEXT
    ranked: bool = False
    data_row_count: int = 0


@dataclass
class ChartLayoutSpec:
    name: str
    section: int
    anchor_cell: str
    allowed_start_row: int
    allowed_end_row: int
    allowed_start_col: int
    allowed_end_col: int
    chart_type: str
    ranked: bool = False


DASHBOARD_SECTION_DEFS: tuple[DashboardSectionDef, ...] = (
    DashboardSectionDef("location", "Inventory Value by Location", "horizontal_bar"),
    DashboardSectionDef("status", "Inventory Exposure by Status", "horizontal_bar"),
    DashboardSectionDef("aging", "Inventory Value by Aging Bucket", "column"),
    DashboardSectionDef(
        "top_excess", "Top 10 Excess Inventory Items", "horizontal_bar", ranked=True
    ),
    DashboardSectionDef("abc_usage", "Annual Usage Value by ABC Class", "column"),
    DashboardSectionDef(
        "replenishment", "Replenishment Requirements by Status", "horizontal_bar"
    ),
    DashboardSectionDef("fill_rate", "Fill Rate by Location", "clustered_bar"),
    DashboardSectionDef(
        "vendor_risk", "Supplier Exposure by Risk Class", "horizontal_bar"
    ),
    DashboardSectionDef(
        "transfer_benefit",
        "Top Transfer Opportunities by Net Benefit",
        "horizontal_bar",
        ranked=True,
    ),
    DashboardSectionDef(
        "action", "Inventory Value by Recommended Action", "horizontal_bar"
    ),
)


def compute_section_layouts(
    data_row_counts: dict[str, int],
    start_row: int = SECTIONS_START_ROW,
) -> list[DashboardSectionLayout]:
    """Compute dynamic section row spans from actual table row counts."""
    layouts: list[DashboardSectionLayout] = []
    current = start_row
    for section_def in DASHBOARD_SECTION_DEFS:
        data_rows = max(1, data_row_counts.get(section_def.key, 1))
        chart_rows = int(CHART_HEIGHT_CM / CHART_CM_PER_EXCEL_ROW) + CHART_BOTTOM_MARGIN_ROWS
        if section_def.key == "fill_rate":
            chart_rows += 4
        body_rows = max(data_rows, chart_rows, MIN_CHART_BODY_ROWS)
        section_rows = 1 + 1 + 1 + body_rows  # title + context + header + data
        end_row = current + section_rows - 1
        layouts.append(
            DashboardSectionLayout(
                key=section_def.key,
                title=section_def.title,
                chart_title=CHART_TITLES[section_def.key],
                chart_type=section_def.chart_type,
                start_row=current,
                end_row=end_row,
                context=section_def.context,
                ranked=section_def.ranked,
                data_row_count=data_rows,
            )
        )
        current = end_row + SECTION_SPACER_ROWS + 1
    return layouts


def chart_height_cm(section_end_row: int, header_row: int) -> float:
    """Size chart to fill the section, leaving CHART_BOTTOM_MARGIN_ROWS above divider."""
    max_chart_end_row = section_end_row - CHART_BOTTOM_MARGIN_ROWS
    usable_rows = max(1, max_chart_end_row - header_row)
    fit_height = usable_rows * CHART_CM_PER_EXCEL_ROW
    return min(CHART_HEIGHT_CM, max(8.0, fit_height))


def chart_layout_specs_from_layouts(
    layouts: list[DashboardSectionLayout],
) -> tuple[ChartLayoutSpec, ...]:
    specs: list[ChartLayoutSpec] = []
    for idx, section in enumerate(layouts, start=1):
        anchor_row = section.start_row + 2
        specs.append(
            ChartLayoutSpec(
                name=section.chart_title,
                section=idx,
                anchor_cell=f"{CHART_ANCHOR_COL}{anchor_row}",
                allowed_start_row=section.start_row,
                allowed_end_row=section.end_row,
                allowed_start_col=CHART_AREA_START_COL,
                allowed_end_col=CHART_AREA_END_COL,
                chart_type=section.chart_type,
                ranked=section.ranked,
            )
        )
    return tuple(specs)


def chart_layout_specs(
    data_row_counts: dict[str, int] | None = None,
) -> tuple[ChartLayoutSpec, ...]:
    """Return chart layout specs; defaults to one row per section when counts omitted."""
    counts = data_row_counts or {s.key: 1 for s in DASHBOARD_SECTION_DEFS}
    layouts = compute_section_layouts(counts)
    return chart_layout_specs_from_layouts(layouts)
