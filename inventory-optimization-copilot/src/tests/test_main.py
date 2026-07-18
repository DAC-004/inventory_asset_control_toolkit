"""Tests for main.py build entry point."""

from pathlib import Path

from config.workbook_config import CSV_FILES
from src.main import ensure_output_directories, main


def test_ensure_output_directories_creates_paths(tmp_path: Path, monkeypatch):
    """Required output folders should be created on demand."""
    dist = tmp_path / "dist"
    generated = tmp_path / "data" / "generated"
    monkeypatch.setattr("src.main.DIST_DIR", dist)
    monkeypatch.setattr("src.main.DATA_GENERATED_DIR", generated)

    ensure_output_directories()

    assert dist.is_dir()
    assert generated.is_dir()


def test_main_returns_success_exit_code(tmp_path: Path, monkeypatch):
    """main() should complete the full build and return 0."""
    dist = tmp_path / "dist"
    generated = tmp_path / "data" / "generated"
    workbook = dist / "Inventory_Optimization_Copilot.xlsx"

    monkeypatch.setattr("src.main.DIST_DIR", dist)
    monkeypatch.setattr("src.main.DATA_GENERATED_DIR", generated)
    monkeypatch.setattr("src.main.WORKBOOK_PATH", workbook)
    monkeypatch.setattr("src.data_generation.pipeline.DATA_GENERATED_DIR", generated)

    assert main() == 0

    assert workbook.exists()
    for filename in CSV_FILES.values():
        assert (generated / filename).exists()
