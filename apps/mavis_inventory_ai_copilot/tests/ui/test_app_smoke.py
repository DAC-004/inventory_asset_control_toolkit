"""Streamlit import and UI smoke tests."""


def test_app_imports_without_error():
    import app  # noqa: F401
    import streamlit_app  # noqa: F401


def test_pages_import_without_error():
    from src.ui.pages import (
        aged_excess,
        ai_summary,
        dashboard,
        data_quality,
        markdown_planner,
        methodology,
        transfer_planner,
    )

    assert all(
        callable(m.render)
        for m in [
            dashboard,
            aged_excess,
            transfer_planner,
            markdown_planner,
            ai_summary,
            data_quality,
            methodology,
        ]
    )
